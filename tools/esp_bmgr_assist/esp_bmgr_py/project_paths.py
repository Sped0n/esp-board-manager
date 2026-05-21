"""Project path helpers shared by assist preflight checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional


def normalize_project_dir(path_value: Any) -> Optional[Path]:
    if path_value is None:
        return None
    value = str(path_value).strip()
    if not value:
        return None
    try:
        return Path(value).expanduser().resolve()
    except OSError:
        return Path(value).expanduser().absolute()


def ensure_existing_directory(path_value: Any) -> Optional[Path]:
    candidate = normalize_project_dir(path_value)
    if candidate is None:
        return None
    if not candidate.exists() or not candidate.is_dir():
        return None
    return candidate


def _global_project_dir(global_args: Any) -> Any:
    if isinstance(global_args, dict):
        return global_args.get('project_dir')
    return getattr(global_args, 'project_dir', None)


def resolve_project_dir(global_args: Any, fallback_project_path: Any, current_dir: Optional[Path] = None) -> Optional[Path]:
    project_dir = ensure_existing_directory(_global_project_dir(global_args))
    if project_dir is not None:
        return project_dir

    fallback = ensure_existing_directory(fallback_project_path)
    if fallback is not None:
        return fallback

    base_dir = current_dir or Path.cwd()
    return ensure_existing_directory(base_dir)


def gen_bmgr_codes_dir(project_dir: Path) -> Path:
    return project_dir / 'components' / 'gen_bmgr_codes'


def board_manager_defaults_path(project_dir: Path) -> Path:
    return gen_bmgr_codes_dir(project_dir) / 'board_manager.defaults'


def sdkconfig_path(project_dir: Path) -> Path:
    return project_dir / 'sdkconfig'


def sdkconfig_defaults_path(project_dir: Path) -> Path:
    return project_dir / 'sdkconfig.defaults'
