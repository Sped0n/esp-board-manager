"""Target mismatch checks for assist preflight."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


def normalize_idf_target(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().strip('"').strip("'").lower().replace('-', '')
    return text or None


def parse_idf_target_from_text(content: str) -> Optional[str]:
    line_re_dq = re.compile(r'^CONFIG_IDF_TARGET="([^"]*)"\s*$')
    line_re_sq = re.compile(r"^CONFIG_IDF_TARGET='([^']*)'\s*$")
    line_re_bare = re.compile(r'^CONFIG_IDF_TARGET=([^#\s]+)\s*$')
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        match = line_re_dq.match(line) or line_re_sq.match(line)
        if match:
            return match.group(1)
        match = line_re_bare.match(line)
        if match:
            return match.group(1).strip('"').strip("'")
    return None


def parse_idf_target_from_file(file_path: Path) -> Optional[str]:
    if not file_path.is_file():
        return None
    try:
        return parse_idf_target_from_text(file_path.read_text(encoding='utf-8'))
    except OSError:
        return None


def find_target_mismatch(defaults_path: Path, sdkconfig_path: Path) -> Optional[str]:
    expected_raw = parse_idf_target_from_file(defaults_path)
    actual_raw = parse_idf_target_from_file(sdkconfig_path)
    if expected_raw is None or actual_raw is None:
        return None

    expected = normalize_idf_target(expected_raw)
    actual = normalize_idf_target(actual_raw)
    if not expected or not actual or expected == actual:
        return None

    return (
        'CONFIG_IDF_TARGET mismatch: sdkconfig has "{actual_raw}" (normalized: {actual}), '
        'board_manager.defaults expects "{expected_raw}" ({expected}). '
        'Run: idf.py set-target {expected} or regenerate with idf.py bmgr -b <board>.'
    ).format(
        actual_raw=actual_raw,
        actual=actual,
        expected_raw=expected_raw,
        expected=expected,
    )
