"""Coverage for stderr notices added by docs/level-2 (A + B) escalation.

These tests pin down the user-visible behavior so a future refactor cannot
silently drop the "real reason" message back into DEBUG-only mode.
"""

import io
import os
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

from esp_bmgr_py import (
    _notice,
    bmgr_discovery,
    bmgr_manifest,
    idf_injector,
    project_integration,
)


def _stub_idf_component_manager_modules() -> dict:
    """Minimal sys.modules stubs so _bootstrap_project_dependencies can import."""
    dep_mod = types.ModuleType('idf_component_manager.dependencies')
    dep_mod.download_project_dependencies = lambda *args, **kwargs: None

    icm_pkg = types.ModuleType('idf_component_manager')
    icm_pkg.dependencies = dep_mod

    mgr_mod = types.ModuleType('idf_component_tools.manager')
    mgr_mod.ManifestManager = type(
        '_ManifestManager',
        (),
        {'__init__': lambda self, *a, **kw: None, 'load': lambda self: None},
    )

    util_mod = types.ModuleType('idf_component_tools.utils')
    util_mod.ProjectRequirements = lambda reqs: reqs

    return {
        'idf_component_manager': icm_pkg,
        'idf_component_manager.dependencies': dep_mod,
        'idf_component_tools.manager': mgr_mod,
        'idf_component_tools.utils': util_mod,
    }


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def _create_project(root: Path) -> None:
    _write(
        root / 'CMakeLists.txt',
        'include($ENV{IDF_PATH}/tools/cmake/project.cmake)\nproject(test)\n',
    )
    (root / 'main').mkdir(parents=True, exist_ok=True)
    _write(root / 'main' / 'CMakeLists.txt', 'idf_component_register(SRCS "main.c")\n')


class NoticeHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        _notice.reset_notice_dedup_for_tests()
        self._env_backup = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env_backup)
        _notice.reset_notice_dedup_for_tests()

    def test_emit_notice_writes_to_stderr_with_tag(self) -> None:
        buf = io.StringIO()
        with redirect_stderr(buf):
            _notice.emit_notice('hello world')
        out = buf.getvalue()
        self.assertIn('[ESP_BMGR_ASSIST]', out)
        self.assertIn('hello world', out)

    def test_emit_notice_dedups_by_key(self) -> None:
        buf = io.StringIO()
        with redirect_stderr(buf):
            _notice.emit_notice('first', dedup_key='k1')
            _notice.emit_notice('first again', dedup_key='k1')
            _notice.emit_notice('different', dedup_key='k2')
        out = buf.getvalue()
        self.assertEqual(out.count('[ESP_BMGR_ASSIST]'), 2)
        self.assertIn('first', out)
        self.assertNotIn('first again', out)
        self.assertIn('different', out)

    def test_emit_notice_without_key_always_prints(self) -> None:
        buf = io.StringIO()
        with redirect_stderr(buf):
            _notice.emit_notice('once')
            _notice.emit_notice('once')
        self.assertEqual(buf.getvalue().count('[ESP_BMGR_ASSIST]'), 2)

    def test_emit_notice_silent_during_shell_completion(self) -> None:
        os.environ['_IDF.PY_COMPLETE'] = 'complete_zsh'
        buf = io.StringIO()
        with redirect_stderr(buf):
            _notice.emit_notice('should not appear')
        self.assertEqual(buf.getvalue(), '')


class ManifestParseFailureNoticeTests(unittest.TestCase):
    def setUp(self) -> None:
        _notice.reset_notice_dedup_for_tests()
        self._env_backup = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env_backup)
        _notice.reset_notice_dedup_for_tests()

    def test_load_dependencies_notices_yaml_syntax_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / 'idf_component.yml'
            # ruamel/pyyaml can both parse this; force a real parser error by
            # using an unbalanced flow mapping.
            _write(manifest, 'dependencies: { not closed\n')

            buf = io.StringIO()
            with redirect_stderr(buf):
                deps = bmgr_manifest.load_dependencies(manifest)

            self.assertEqual(deps, {})
            out = buf.getvalue()
            self.assertIn('[ESP_BMGR_ASSIST]', out)
            self.assertIn(str(manifest), out)
            self.assertIn('Failed to parse manifest', out)

    def test_load_dependencies_does_not_notice_missing_file(self) -> None:
        # Missing file is normal flow (FileNotFoundError branch) -- no notice.
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / 'idf_component.yml'
            buf = io.StringIO()
            with redirect_stderr(buf):
                deps = bmgr_manifest.load_dependencies(manifest)
            self.assertEqual(deps, {})
            self.assertEqual(buf.getvalue(), '')

    def test_manifest_declares_board_manager_notices_yaml_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            _create_project(project)
            _write(project / 'main' / 'idf_component.yml', 'dependencies: { broken\n')

            buf = io.StringIO()
            with redirect_stderr(buf):
                declared = project_integration.manifest_declares_board_manager(project)

            self.assertFalse(declared)
            self.assertIn('Failed to parse manifest', buf.getvalue())

    def test_manifest_parse_notice_dedups_across_modules(self) -> None:
        # bmgr_manifest.load_dependencies and project_integration.manifest_declares_board_manager
        # both share the same dedup key for the same manifest path; only the
        # first call should print, the second is silently dropped.
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            _create_project(project)
            manifest = project / 'main' / 'idf_component.yml'
            _write(manifest, 'dependencies: { broken\n')

            buf = io.StringIO()
            with redirect_stderr(buf):
                bmgr_manifest.load_dependencies(manifest)
                project_integration.manifest_declares_board_manager(project)

            self.assertEqual(buf.getvalue().count('Failed to parse manifest'), 1)


class LockParseFailureNoticeTests(unittest.TestCase):
    def setUp(self) -> None:
        _notice.reset_notice_dedup_for_tests()

    def tearDown(self) -> None:
        _notice.reset_notice_dedup_for_tests()

    def test_find_bmgr_from_lock_notices_yaml_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            lock = project / 'dependencies.lock'
            _write(lock, 'dependencies: { broken\n')

            buf = io.StringIO()
            with redirect_stderr(buf):
                result = bmgr_discovery.find_bmgr_from_lock(project)

            self.assertIsNone(result)
            out = buf.getvalue()
            self.assertIn('Failed to parse lock file', out)
            self.assertIn(str(lock), out)


class BootstrapSkipNoticeTests(unittest.TestCase):
    def setUp(self) -> None:
        _notice.reset_notice_dedup_for_tests()
        self._env_backup = dict(os.environ)
        idf_injector._MAIN_EXECUTED = False

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._env_backup)
        idf_injector._MAIN_EXECUTED = False
        _notice.reset_notice_dedup_for_tests()

    def test_not_a_project_notices_when_user_invokes_bmgr(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            non_project = Path(temp_dir) / 'not_a_project'
            non_project.mkdir()
            context = idf_injector.CliContext(
                True, non_project, False, ('idf.py', 'bmgr', '-l'), bmgr_command='bmgr'
            )

            buf = io.StringIO()
            with redirect_stderr(buf):
                idf_injector._bootstrap_for_context(context)

            out = buf.getvalue()
            self.assertIn('not an ESP-IDF project root', out)
            self.assertIn(str(non_project), out)
            self.assertIn('Skipped bmgr bootstrap', out)

    def test_not_a_project_stays_quiet_when_cwd_is_bmgr_component(self) -> None:
        # bmgr-developer workflow: run `idf.py bmgr -l` from inside
        # esp_board_manager/ itself.  cwd is not an ESP-IDF project, but it IS
        # a valid bmgr component, so bmgr usually still works via cwd discovery.
        with tempfile.TemporaryDirectory() as temp_dir:
            bmgr_component = Path(temp_dir) / 'esp_board_manager'
            bmgr_component.mkdir()
            for required in ('idf_ext.py', 'idf_component.yml', 'gen_bmgr_config_codes.py'):
                _write(bmgr_component / required, '')
            context = idf_injector.CliContext(
                True, bmgr_component, False, ('idf.py', 'bmgr', '-l'), bmgr_command='bmgr'
            )

            buf = io.StringIO()
            with redirect_stderr(buf):
                idf_injector._bootstrap_for_context(context)

            self.assertNotIn('[ESP_BMGR_ASSIST]', buf.getvalue())

    def test_not_a_project_stays_quiet_for_non_bmgr_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            non_project = Path(temp_dir) / 'not_a_project'
            non_project.mkdir()
            context = idf_injector.CliContext(
                True, non_project, False, ('idf.py', 'build'), bmgr_command=None
            )

            buf = io.StringIO()
            with redirect_stderr(buf):
                idf_injector._bootstrap_for_context(context)

            self.assertNotIn('[ESP_BMGR_ASSIST]', buf.getvalue())

    def test_bootstrap_project_dependencies_notices_when_no_manifest_found(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            # Real project layout (CMakeLists.txt + main/) but NO idf_component.yml,
            # NO components/.  _load_project_manifests must come back empty.
            _create_project(project)

            buf = io.StringIO()
            with mock.patch.dict(sys.modules, _stub_idf_component_manager_modules()):
                with mock.patch.object(idf_injector, '_load_project_manifests', return_value=[]):
                    with redirect_stderr(buf):
                        idf_injector._bootstrap_project_dependencies(project)

            out = buf.getvalue()
            self.assertIn('No idf_component.yml found', out)
            self.assertIn(str(project), out)


if __name__ == '__main__':
    unittest.main()
