import io
import json
import os
import tempfile
import time
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

from esp_bmgr_py import update_check


class UpdateCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env_backup = dict(os.environ)
        update_check._update_thread_started = False
        update_check._warned_latest_version = None

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env_backup)
        update_check._update_thread_started = False
        update_check._warned_latest_version = None

    def test_fresh_cache_with_newer_version_warns_immediately(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['XDG_CACHE_HOME'] = temp_dir
            update_check._write_cache(
                {
                    'checked_at': time.time(),
                    'latest_version': '9.9.9',
                }
            )

            output = io.StringIO()
            with mock.patch.object(update_check, '_spawn_refresh_thread') as mocked_refresh:
                with redirect_stderr(output):
                    update_check.maybe_warn_about_update('bmgr')

            self.assertIn(
                f'Update available: {update_check.__version__} -> 9.9.9',
                output.getvalue(),
            )
            mocked_refresh.assert_not_called()

    def test_fresh_cache_without_newer_version_stays_silent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['XDG_CACHE_HOME'] = temp_dir
            update_check._write_cache(
                {
                    'checked_at': time.time(),
                    'latest_version': update_check.__version__,
                }
            )

            output = io.StringIO()
            with mock.patch.object(update_check, '_spawn_refresh_thread') as mocked_refresh:
                with redirect_stderr(output):
                    update_check.maybe_warn_about_update('bmgr')

            self.assertEqual(output.getvalue(), '')
            mocked_refresh.assert_not_called()

    def test_stale_cache_schedules_background_refresh(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['XDG_CACHE_HOME'] = temp_dir
            update_check._write_cache(
                {
                    'checked_at': 0,
                    'latest_version': update_check.__version__,
                }
            )

            with mock.patch.object(update_check, '_spawn_refresh_thread') as mocked_refresh:
                update_check.maybe_warn_about_update('bmgr')

            mocked_refresh.assert_called_once_with(update_check.__version__)

    def test_force_env_schedules_refresh_even_with_fresh_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['XDG_CACHE_HOME'] = temp_dir
            os.environ[update_check.FORCE_UPDATE_CHECK_ENV] = '1'
            update_check._write_cache(
                {
                    'checked_at': time.time(),
                    'latest_version': update_check.__version__,
                }
            )

            with mock.patch.object(update_check, '_spawn_refresh_thread') as mocked_refresh:
                update_check.maybe_warn_about_update('bmgr')

            mocked_refresh.assert_called_once_with(update_check.__version__)

    def test_disable_env_skips_check(self) -> None:
        os.environ[update_check.DISABLE_UPDATE_CHECK_ENV] = '1'
        with mock.patch.object(update_check, '_spawn_refresh_thread') as mocked_refresh:
            update_check.maybe_warn_about_update('bmgr')
        mocked_refresh.assert_not_called()

    def test_non_bmgr_command_is_ignored(self) -> None:
        with mock.patch.object(update_check, '_spawn_refresh_thread') as mocked_refresh:
            update_check.maybe_warn_about_update('build')
        mocked_refresh.assert_not_called()

    def test_refresh_worker_writes_cache_and_warns_on_newer_version(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / 'update-check.json'
            output = io.StringIO()

            with redirect_stderr(output):
                update_check._refresh_cache_and_warn(
                    current_version='0.8.0',
                    cache_path=cache_path,
                    fetcher=lambda: '9.9.9',
                )

            cache = json.loads(cache_path.read_text(encoding='utf-8'))
            self.assertEqual(cache['latest_version'], '9.9.9')
            self.assertIn('checked_at', cache)
            self.assertIn('Update available: 0.8.0 -> 9.9.9', output.getvalue())

    def test_pypi_url_override_via_env(self) -> None:
        os.environ.pop(update_check.PYPI_JSON_URL_ENV, None)
        self.assertEqual(
            update_check._resolve_pypi_json_url(),
            update_check.DEFAULT_PYPI_JSON_URL,
        )

        custom = 'https://test.pypi.org/pypi/esp-bmgr-assist/json'
        os.environ[update_check.PYPI_JSON_URL_ENV] = custom
        self.assertEqual(update_check._resolve_pypi_json_url(), custom)

        # Whitespace-only or empty value should fall back to the default rather
        # than fetch from a malformed URL.
        os.environ[update_check.PYPI_JSON_URL_ENV] = '   '
        self.assertEqual(
            update_check._resolve_pypi_json_url(),
            update_check.DEFAULT_PYPI_JSON_URL,
        )

    def test_fetch_latest_version_honours_override_env(self) -> None:
        os.environ[update_check.PYPI_JSON_URL_ENV] = (
            'https://test.pypi.org/pypi/esp-bmgr-assist/json'
        )

        captured = {}

        class _FakeResponse:
            def __init__(self, body: bytes) -> None:
                self._body = body

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return self._body

        def fake_urlopen(url, timeout):
            captured['url'] = url
            captured['timeout'] = timeout
            return _FakeResponse(b'{"info": {"version": "9.9.9"}}')

        with mock.patch.object(update_check, 'urlopen', side_effect=fake_urlopen):
            result = update_check._fetch_latest_version()

        self.assertEqual(result, '9.9.9')
        self.assertEqual(
            captured['url'],
            'https://test.pypi.org/pypi/esp-bmgr-assist/json',
        )

    def test_refresh_worker_swallows_fetch_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / 'update-check.json'
            output = io.StringIO()

            def _raise():
                raise TimeoutError('timeout')

            with redirect_stderr(output):
                update_check._refresh_cache_and_warn(
                    current_version='0.8.0',
                    cache_path=cache_path,
                    fetcher=_raise,
                )

            cache = json.loads(cache_path.read_text(encoding='utf-8'))
            self.assertIsNone(cache['latest_version'])
            self.assertIn('checked_at', cache)
            self.assertEqual(output.getvalue(), '')
