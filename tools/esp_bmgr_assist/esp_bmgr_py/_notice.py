"""Process-wide stderr notices for esp-bmgr-assist.

`emit_notice` writes user-visible messages without requiring ``ESP_BMGR_DEBUG=1``.
Use it for cases where the assist intentionally backs off (parse failure, project
layout mismatch, etc.) and the user would otherwise see a misleading downstream
error such as ``Project does not depend on esp_board_manager`` or
``No such option: -b``.

Notices are de-duplicated **within a single Python process** using ``dedup_key``.
Across the multiple short-lived interpreters that ``idf.py`` and component
manager spawn the same notice may still appear more than once; that is an
acceptable trade-off versus needing on-disk state.
"""

from __future__ import annotations

import os
import sys
from typing import Optional, Set


ASSIST_TAG = '[ESP_BMGR_ASSIST]'

_NOTICE_KEYS: Set[str] = set()


def _is_shell_completion_invocation() -> bool:
    return bool(os.environ.get('_IDF.PY_COMPLETE'))


def emit_notice(message: str, *, dedup_key: Optional[str] = None) -> None:
    """Print ``message`` to stderr with the assist tag, deduped per process.

    Args:
        message: Human-readable notice without trailing newline. The
            ``[ESP_BMGR_ASSIST]`` tag is prepended automatically.
        dedup_key: Optional process-local key. The first call with a given key
            prints; subsequent calls with the same key are silently dropped.
            Pass ``None`` to always print.
    """
    if _is_shell_completion_invocation():
        return
    if dedup_key is not None:
        if dedup_key in _NOTICE_KEYS:
            return
        _NOTICE_KEYS.add(dedup_key)
    print(f'{ASSIST_TAG} {message}', file=sys.stderr, flush=True)


def reset_notice_dedup_for_tests() -> None:
    """Clear the dedup state. Test-only entry point."""
    _NOTICE_KEYS.clear()
