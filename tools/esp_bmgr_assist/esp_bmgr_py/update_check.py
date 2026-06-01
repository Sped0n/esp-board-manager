"""Best-effort update notification for esp-bmgr-assist.

This module is intentionally lightweight:
- no extra dependencies beyond the stdlib
- cache-first behavior
- stale cache refresh happens in a daemon thread
- network failures never block or fail the command
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from urllib.request import urlopen

from esp_bmgr_py import __version__


PACKAGE_NAME = 'esp-bmgr-assist'
DEFAULT_PYPI_JSON_URL = f'https://pypi.org/pypi/{PACKAGE_NAME}/json'
UPDATE_TAG = '[ESP_BMGR_ASSIST]'
DISABLE_UPDATE_CHECK_ENV = 'ESP_BMGR_DISABLE_UPDATE_CHECK'
FORCE_UPDATE_CHECK_ENV = 'ESP_BMGR_FORCE_UPDATE_CHECK'
UPDATE_CHECK_TTL_ENV = 'ESP_BMGR_UPDATE_CHECK_TTL_SEC'
PYPI_JSON_URL_ENV = 'ESP_BMGR_PYPI_JSON_URL'
DEFAULT_UPDATE_CHECK_TTL_SEC = 24 * 60 * 60
NETWORK_TIMEOUT_SEC = 0.7


def _resolve_pypi_json_url() -> str:
    """Allow tests / TestPyPI rehearsal to redirect the version-check endpoint.

    Resolved every call (rather than snapshotted at import time) so that setting
    ``ESP_BMGR_PYPI_JSON_URL`` for a single command takes effect without reloading
    the module.
    """
    override = os.environ.get(PYPI_JSON_URL_ENV)
    if override and override.strip():
        return override.strip()
    return DEFAULT_PYPI_JSON_URL

_update_thread_started = False
_warned_latest_version: Optional[str] = None


def _env_flag_true(var_name: str) -> bool:
    value = os.environ.get(var_name, '')
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def _cache_root() -> Path:
    xdg_cache = os.environ.get('XDG_CACHE_HOME')
    if xdg_cache:
        return Path(xdg_cache).expanduser()
    return Path.home() / '.cache'


def _cache_file() -> Path:
    return _cache_root() / PACKAGE_NAME / 'update-check.json'


def _ttl_seconds() -> int:
    raw = os.environ.get(UPDATE_CHECK_TTL_ENV)
    if raw:
        try:
            parsed = int(raw)
            if parsed >= 0:
                return parsed
        except ValueError:
            pass
    return DEFAULT_UPDATE_CHECK_TTL_SEC


def _load_cache(path: Optional[Path] = None) -> Dict[str, Any]:
    target = path or _cache_file()
    try:
        return json.loads(target.read_text(encoding='utf-8'))
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError):
        return {}


def _write_cache(cache: Dict[str, Any], path: Optional[Path] = None) -> None:
    target = path or _cache_file()
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=str(target.parent),
            prefix='update-check-',
            suffix='.json',
            delete=False,
        ) as tmp:
            json.dump(cache, tmp, ensure_ascii=True, sort_keys=True)
            tmp.write('\n')
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, target)
    except OSError:
        try:
            if 'tmp_path' in locals():
                tmp_path.unlink(missing_ok=True)
        except OSError:
            pass


def _cache_is_fresh(cache: Dict[str, Any]) -> bool:
    checked_at = cache.get('checked_at')
    if not isinstance(checked_at, (int, float)):
        return False
    ttl = _ttl_seconds()
    if ttl <= 0:
        return False
    return (time.time() - float(checked_at)) < ttl


def _version_key(version: str):
    try:
        from packaging.version import Version

        return Version(version)
    except Exception:
        parts = tuple(int(part) for part in re.findall(r'\d+', version))
        return parts


def _is_newer_version(latest_version: str, current_version: str) -> bool:
    try:
        return _version_key(latest_version) > _version_key(current_version)
    except Exception:
        return latest_version != current_version


def _emit_update_message(latest_version: str, current_version: str) -> None:
    global _warned_latest_version
    if _warned_latest_version == latest_version:
        return
    _warned_latest_version = latest_version
    print(
        f'{UPDATE_TAG} Update available: {current_version} -> {latest_version}. '
        f'Run: python3 -m pip install --upgrade {PACKAGE_NAME}',
        file=sys.stderr,
        flush=True,
    )


def _fetch_latest_version(url: Optional[str] = None, timeout: float = NETWORK_TIMEOUT_SEC) -> Optional[str]:
    target_url = url or _resolve_pypi_json_url()
    with urlopen(target_url, timeout=timeout) as response:
        payload = json.loads(response.read().decode('utf-8'))
    info = payload.get('info', {})
    version = info.get('version')
    if isinstance(version, str) and version.strip():
        return version.strip()
    return None


def _refresh_cache_and_warn(
    *,
    current_version: str,
    cache_path: Optional[Path] = None,
    fetcher: Callable[[], Optional[str]] = _fetch_latest_version,
) -> None:
    latest_version = None
    try:
        latest_version = fetcher()
    except Exception:
        latest_version = None

    cache = {
        'checked_at': time.time(),
        'latest_version': latest_version,
    }
    _write_cache(cache, path=cache_path)

    if isinstance(latest_version, str) and _is_newer_version(latest_version, current_version):
        _emit_update_message(latest_version, current_version)


def _spawn_refresh_thread(current_version: str) -> None:
    global _update_thread_started
    if _update_thread_started:
        return
    _update_thread_started = True

    thread = threading.Thread(
        target=_refresh_cache_and_warn,
        kwargs={'current_version': current_version},
        name='esp-bmgr-assist-update-check',
        daemon=True,
    )
    thread.start()


def maybe_warn_about_update(command: Optional[str]) -> None:
    if command not in {'bmgr', 'gen-bmgr-config'}:
        return
    if _env_flag_true(DISABLE_UPDATE_CHECK_ENV):
        return

    current_version = __version__
    cache = _load_cache()
    latest_version = cache.get('latest_version')
    if isinstance(latest_version, str) and _is_newer_version(latest_version, current_version):
        _emit_update_message(latest_version, current_version)

    if not _env_flag_true(FORCE_UPDATE_CHECK_ENV) and _cache_is_fresh(cache):
        return

    _spawn_refresh_thread(current_version)
