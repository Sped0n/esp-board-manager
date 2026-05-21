"""Resolve a reasonable ``IDF_TARGET`` for early bootstrap before CMake has run."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Mapping, Optional

from esp_bmgr_py.project_paths import (
    board_manager_defaults_path,
    sdkconfig_defaults_path,
    sdkconfig_path,
)
from esp_bmgr_py.target_check import normalize_idf_target, parse_idf_target_from_file


BOOTSTRAP_TARGET_ENV = 'ESP_BMGR_BOOTSTRAP_TARGET'
DEFAULT_BOOTSTRAP_IDF_TARGET = 'esp32'


@dataclass(frozen=True)
class BootstrapTargetResult:
    target: str
    source: str
    is_fallback: bool


def _normalize_candidate(value: Optional[str]) -> Optional[str]:
    return normalize_idf_target(value)


def _target_from_project_files(project_path: Path) -> Optional[BootstrapTargetResult]:
    for source, path in (
        ('sdkconfig', sdkconfig_path(project_path)),
        ('sdkconfig.defaults', sdkconfig_defaults_path(project_path)),
        ('board_manager.defaults', board_manager_defaults_path(project_path)),
    ):
        target = _normalize_candidate(parse_idf_target_from_file(path))
        if target:
            return BootstrapTargetResult(target=target, source=source, is_fallback=False)
    return None


def resolve_bootstrap_target(
    project_path: Path,
    env: Optional[Mapping[str, str]] = None,
) -> BootstrapTargetResult:
    environment = env if env is not None else os.environ

    existing_target = _normalize_candidate(environment.get('IDF_TARGET'))
    if existing_target:
        return BootstrapTargetResult(
            target=existing_target,
            source='env:IDF_TARGET',
            is_fallback=False,
        )

    override_target = _normalize_candidate(environment.get(BOOTSTRAP_TARGET_ENV))
    if override_target:
        return BootstrapTargetResult(
            target=override_target,
            source=f'env:{BOOTSTRAP_TARGET_ENV}',
            is_fallback=False,
        )

    project_target = _target_from_project_files(project_path)
    if project_target is not None:
        return project_target

    return BootstrapTargetResult(
        target=DEFAULT_BOOTSTRAP_IDF_TARGET,
        source='fallback-default',
        is_fallback=True,
    )
