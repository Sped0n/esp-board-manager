"""Generated artifact checks for assist preflight."""

from __future__ import annotations

from pathlib import Path
from typing import List

from esp_bmgr_py.project_paths import gen_bmgr_codes_dir


REQUIRED_GEN_BMGR_CODE_FILES = (
    'CMakeLists.txt',
    'idf_component.yml',
    'board_manager.defaults',
    'gen_board_info.c',
    'gen_board_periph_config.c',
    'gen_board_periph_handles.c',
    'gen_board_device_config.c',
    'gen_board_device_handles.c',
)


def list_missing_gen_files(project_dir: Path) -> List[str]:
    base = gen_bmgr_codes_dir(project_dir)
    missing = []
    for name in REQUIRED_GEN_BMGR_CODE_FILES:
        if not (base / name).is_file():
            missing.append(name)
    return missing
