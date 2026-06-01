"""Shared manifest helpers for ESP Board Manager detection and bootstrap."""

from __future__ import annotations

import codecs
import os
import sys
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

from esp_bmgr_py._notice import emit_notice


MANIFEST_NAMES = ('idf_component.yml', 'idf_component.yaml')
BMGR_KEYS = ('espressif/esp_board_manager', 'esp_board_manager')
CANONICAL_BMGR_KEY = 'espressif/esp_board_manager'
_YAML_MODULE = None


def _emit_manifest_debug(message: str) -> None:
    """Surface swallowed parse/IO errors when ``ESP_BMGR_DEBUG=1`` is set.

    ``load_dependencies`` intentionally keeps tolerant behavior for its legacy callers
    (returning ``{}`` on failure), but silently swallowing exceptions used to make YAML
    syntax errors invisible -- the caller then behaved as if the manifest declared no
    dependencies, which cascaded into misleading downstream errors.
    """
    if os.environ.get('ESP_BMGR_DEBUG', '0') == '1':
        print(f'[ESP_BMGR_ASSIST] {message}', file=sys.stderr, flush=True)


def _require_pyyaml():
    global _YAML_MODULE
    if _YAML_MODULE is None:
        try:
            import yaml as yaml_module
        except ImportError as exc:
            raise RuntimeError(
                'PyYAML is required when esp-bmgr-assist needs to inspect manifests or dependencies.lock. '
                'Install esp-bmgr-assist with dependencies or add `pyyaml` to this Python environment.'
            ) from exc
        _YAML_MODULE = yaml_module
    return _YAML_MODULE


def find_component_manifest(component_path: Path) -> Optional[Path]:
    for name in MANIFEST_NAMES:
        manifest_path = component_path / name
        if manifest_path.exists():
            return manifest_path
    return None


def find_project_manifest(project_path: Path) -> Optional[Path]:
    return find_component_manifest(project_path / 'main')


def read_manifest_text(manifest_path: Path) -> Tuple[str, str, bool]:
    raw = manifest_path.read_bytes()
    has_bom = raw.startswith(codecs.BOM_UTF8)
    newline = '\r\n' if b'\r\n' in raw else '\n'
    text = raw.decode('utf-8-sig' if has_bom else 'utf-8')
    return text, newline, has_bom


def load_manifest_document(manifest_path: Path) -> Tuple[Dict[str, Any], str, bool, str]:
    backend = 'yaml'
    if manifest_path.exists():
        text, newline, has_bom = read_manifest_text(manifest_path)
    else:
        text, newline, has_bom = '', os.linesep, False

    try:
        from ruamel.yaml import YAML

        backend = 'ruamel'
        yaml_runtime = YAML()
        yaml_runtime.preserve_quotes = True
        yaml_runtime.indent(mapping=2, sequence=4, offset=2)
        data = yaml_runtime.load(text) if text else None
    except ImportError:
        data = _require_pyyaml().safe_load(text) if text else None

    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise RuntimeError(f'Manifest {manifest_path} must contain a top-level mapping')
    return data, newline, has_bom, backend


def safe_load_yaml_text(text: str) -> Any:
    return _require_pyyaml().safe_load(text)


def load_dependencies(manifest_path: Path) -> Dict[str, Any]:
    try:
        data, _, _, _ = load_manifest_document(manifest_path)
    except FileNotFoundError:
        return {}
    except Exception as exc:
        _emit_manifest_debug(
            f'load_dependencies: swallowed {type(exc).__name__} while parsing '
            f'{manifest_path}: {exc}'
        )
        # Without this notice, a YAML/IO failure here silently demotes the
        # manifest to "declares no dependencies", and the user later sees the
        # very misleading "Project does not depend on esp_board_manager"
        # instead of the real syntax/permission error.
        emit_notice(
            f'Failed to parse manifest {manifest_path}: '
            f'{type(exc).__name__}: {exc}. '
            f'Treating it as if it declared no dependencies.',
            dedup_key=f'manifest-parse:{manifest_path}',
        )
        return {}

    dependencies = data.get('dependencies', {})
    return dependencies if isinstance(dependencies, dict) else {}


def find_bmgr_dependency(dependencies: Mapping[str, Any]) -> Optional[Tuple[str, Any]]:
    for key in BMGR_KEYS:
        if key in dependencies:
            return key, dependencies[key]
    return None
