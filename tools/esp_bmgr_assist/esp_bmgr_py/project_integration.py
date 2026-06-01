"""Project-level board manager usage detection for assist preflight."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from esp_bmgr_py._notice import emit_notice
from esp_bmgr_py.bmgr_discovery import find_board_manager_component
from esp_bmgr_py.bmgr_manifest import (
    find_bmgr_dependency,
    find_project_manifest,
    load_manifest_document,
)


def _emit_integration_debug(message: str) -> None:
    if os.environ.get('ESP_BMGR_DEBUG', '0') == '1':
        print(f'[ESP_BMGR_ASSIST] {message}', file=sys.stderr, flush=True)


def find_board_manager_root(project_path: Path):
    return find_board_manager_component(project_path)


def manifest_declares_board_manager(project_path: Path) -> bool:
    manifest_path = find_project_manifest(project_path)
    if manifest_path is None:
        return False
    try:
        data, _newline, _has_bom, _backend = load_manifest_document(manifest_path)
    except FileNotFoundError:
        return False
    except Exception as exc:
        _emit_integration_debug(
            f'manifest_declares_board_manager: swallowed {type(exc).__name__} '
            f'while parsing {manifest_path}: {exc}'
        )
        # Shared dedup key with bmgr_manifest.load_dependencies: both code paths
        # hit the same manifest, so a single visible notice per file is enough.
        emit_notice(
            f'Failed to parse manifest {manifest_path}: '
            f'{type(exc).__name__}: {exc}. '
            f'Treating it as if it declared no dependencies.',
            dedup_key=f'manifest-parse:{manifest_path}',
        )
        return False
    dependencies = data.get('dependencies', {})
    if not isinstance(dependencies, dict):
        return False
    return find_bmgr_dependency(dependencies) is not None


def project_uses_board_manager(project_path: Path) -> bool:
    if not project_path.is_dir():
        return False
    if find_board_manager_root(project_path) is not None:
        return True
    return manifest_declares_board_manager(project_path)
