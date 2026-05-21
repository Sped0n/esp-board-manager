"""Shared helpers for locating ESP Board Manager components in a project."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, List, Optional, Sequence, Tuple

from esp_bmgr_py._notice import emit_notice
from esp_bmgr_py.bmgr_manifest import (
    BMGR_KEYS,
    CANONICAL_BMGR_KEY,
    find_bmgr_dependency,
    find_component_manifest,
    find_project_manifest,
    load_dependencies,
    safe_load_yaml_text,
)


BMGR_REQUIRED_FILES = ('idf_ext.py', 'idf_component.yml', 'gen_bmgr_config_codes.py')
BMGR_COMPONENT_DIRS = ('esp_board_manager', 'espressif__esp_board_manager')
MANAGED_BMGR_DIR = ('managed_components', 'espressif__esp_board_manager')


DebugOnce = Optional[Callable[[str, Path, str], None]]
Debug = Optional[Callable[[str], None]]


def _emit_debug_once(debug_once: DebugOnce, kind: str, path: Path, message: str) -> None:
    if debug_once is not None:
        debug_once(kind, path, message)


def _emit_debug(debug: Debug, message: str) -> None:
    if debug is not None:
        debug(message)


def resolve_manifest_relative_path(manifest_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (manifest_path.parent / candidate).resolve()


def resolve_override_path(manifest_path: Path, override_path: str) -> Path:
    return resolve_manifest_relative_path(manifest_path, override_path)


def resolve_declared_local_bmgr(
    manifest_path: Path, dependency: Any
) -> Optional[Tuple[str, Path]]:
    if not isinstance(dependency, dict) or dependency.get('git'):
        return None

    if dependency.get('override_path'):
        return (
            'override_path',
            resolve_manifest_relative_path(manifest_path, str(dependency['override_path'])),
        )

    if dependency.get('path'):
        return (
            'path',
            resolve_manifest_relative_path(manifest_path, str(dependency['path'])),
        )

    return None


def is_bmgr_component(path: Path) -> bool:
    return path.is_dir() and all((path / name).exists() for name in BMGR_REQUIRED_FILES)


def find_local_bmgr(project_path: Path, *, debug_once: DebugOnce = None) -> Optional[Path]:
    for _name, component_path in collect_local_components(project_path):
        manifest_path = find_component_manifest(component_path)
        if manifest_path is None:
            continue
        dependencies = load_dependencies(manifest_path)
        result = find_bmgr_dependency(dependencies)
        if result is None:
            continue

        _key, dependency = result
        local_decl = resolve_declared_local_bmgr(manifest_path, dependency)
        if local_decl is None:
            continue

        field_name, candidate = local_decl
        if is_bmgr_component(candidate):
            _emit_debug_once(
                debug_once,
                f'{field_name}_ok',
                candidate,
                f'Found local board manager via {field_name}: {candidate}',
            )
            return candidate
        _emit_debug_once(
            debug_once,
            f'{field_name}_bad',
            candidate,
            f'Ignoring invalid {field_name} for board manager: {candidate}',
        )

    if project_path.name.casefold() == 'test_apps' and is_bmgr_component(project_path.parent):
        resolved = project_path.parent.resolve()
        _emit_debug_once(debug_once, 'test_apps_parent', resolved, f'Found board manager at parent of test_apps: {resolved}')
        return resolved

    components_dir = project_path / 'components'
    for component_dir in BMGR_COMPONENT_DIRS:
        candidate = components_dir / component_dir
        if is_bmgr_component(candidate):
            resolved = candidate.resolve()
            _emit_debug_once(debug_once, 'components', resolved, f'Found local board manager in components: {candidate}')
            return resolved
    return None


def find_managed_bmgr(project_path: Path, *, debug_once: DebugOnce = None) -> Optional[Path]:
    candidate = project_path.joinpath(*MANAGED_BMGR_DIR)
    if is_bmgr_component(candidate):
        resolved = candidate.resolve()
        _emit_debug_once(debug_once, 'managed', resolved, f'Found managed board manager: {candidate}')
        return resolved
    return None


def collect_local_components(project_path: Path, *, skip_components: Sequence[str] = ()) -> List[Tuple[str, Path]]:
    components: List[Tuple[str, Path]] = []

    main_dir = project_path / 'main'
    if main_dir.is_dir():
        components.append(('main', main_dir))

    components_dir = project_path / 'components'
    if components_dir.is_dir():
        for item in sorted(components_dir.iterdir(), key=lambda path: path.name):
            if item.is_dir() and item.name not in skip_components:
                components.append((item.name, item))

    return components


def load_project_manifests(project_path: Path, *, skip_components: Sequence[str] = ()):
    try:
        from idf_component_tools.manager import ManifestManager
    except ImportError as exc:
        raise RuntimeError(
            'idf-component-manager is required to resolve project dependencies for bmgr/gen-bmgr-config'
        ) from exc

    manifests = []
    for name, component_path in collect_local_components(project_path, skip_components=skip_components):
        manifest_path = find_component_manifest(component_path)
        if not manifest_path:
            continue
        if not (component_path / 'CMakeLists.txt').is_file():
            continue
        manifests.append(ManifestManager(str(component_path), name).load())

    return manifests


def find_bmgr_from_lock(project_path: Path, *, debug: Debug = None, debug_once: DebugOnce = None) -> Optional[Path]:
    lock_path = project_path / 'dependencies.lock'
    if not lock_path.is_file():
        return None

    try:
        lock_data = safe_load_yaml_text(lock_path.read_text(encoding='utf-8')) or {}
    except Exception as exc:
        _emit_debug(debug, f'Failed to inspect {lock_path}: {exc}')
        emit_notice(
            f'Failed to parse lock file {lock_path}: '
            f'{type(exc).__name__}: {exc}.',
            dedup_key=f'lock-parse:{lock_path}',
        )
        return None

    dependencies = lock_data.get('dependencies')
    if not isinstance(dependencies, dict):
        return None

    for name in (CANONICAL_BMGR_KEY, *BMGR_KEYS):
        solved = dependencies.get(name)
        if not isinstance(solved, dict):
            continue

        source = solved.get('source')
        if isinstance(source, dict) and source.get('type') == 'local':
            raw_path = source.get('path')
            if not raw_path:
                continue
            try:
                candidate = Path(str(raw_path)).expanduser()
                if not candidate.is_absolute():
                    candidate = (lock_path.parent / candidate).resolve()
                else:
                    candidate = candidate.resolve()
            except Exception as exc:
                _emit_debug(debug, f'Failed to resolve local board manager path from lock file: {exc}')
                emit_notice(
                    f'Could not resolve local board manager path from {lock_path} '
                    f'(entry {name!r}, raw path {raw_path!r}): '
                    f'{type(exc).__name__}: {exc}.',
                    dedup_key=f'lock-path-resolve:{lock_path}:{name}',
                )
                continue
            if is_bmgr_component(candidate):
                _emit_debug_once(debug_once, 'lock_local', candidate, f'Found board manager from dependencies.lock: {candidate}')
                return candidate
            _emit_debug_once(debug_once, 'lock_local_bad', candidate, f'Ignoring invalid local board manager from dependencies.lock: {candidate}')
            continue

        managed_candidate = find_managed_bmgr(project_path, debug_once=debug_once)
        if managed_candidate:
            return managed_candidate

    return None


def find_board_manager_component(project_path: Path, *, debug: Debug = None, debug_once: DebugOnce = None) -> Optional[Path]:
    for locator in (
        lambda path: find_local_bmgr(path, debug_once=debug_once),
        lambda path: find_bmgr_from_lock(path, debug=debug, debug_once=debug_once),
        lambda path: find_managed_bmgr(path, debug_once=debug_once),
    ):
        candidate = locator(project_path)
        if candidate:
            return candidate
    _emit_debug_once(
        debug_once,
        'layer0_miss',
        project_path,
        f'Layer 0 miss: no board manager under {project_path} '
        f'(tried override_path / local path / components/esp_board_manager / '
        f'components/espressif__esp_board_manager / dependencies.lock / '
        f'managed_components/espressif__esp_board_manager)',
    )
    return None
