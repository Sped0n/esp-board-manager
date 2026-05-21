"""Shared helpers for identifying bmgr-related CLI requests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


BMGR_ACTION_NAMES = frozenset(('bmgr', 'gen-bmgr-config'))


@dataclass(frozen=True)
class BmgrRequest:
    command: Optional[str]
    is_bmgr_cli: bool
    is_legacy_command: bool


def resolve_bmgr_command(argv: Iterable[str]) -> Optional[str]:
    args = list(argv)[1:]
    return next((token for token in args if token in BMGR_ACTION_NAMES), None)


def resolve_bmgr_request(argv: Iterable[str]) -> BmgrRequest:
    command = resolve_bmgr_command(argv)
    return BmgrRequest(
        command=command,
        is_bmgr_cli=command is not None,
        is_legacy_command=command == 'gen-bmgr-config',
    )
