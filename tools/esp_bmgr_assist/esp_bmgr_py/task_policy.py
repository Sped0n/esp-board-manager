"""Task classification helpers for assist-side preflight checks.

The task groups intentionally mirror the current ESP Board Manager command taxonomy so assist
can make the same high-level decisions without importing component-local code.
"""

from __future__ import annotations

from typing import Iterable, Optional, Sequence, Tuple


BMGR_COMMAND_TASKS = frozenset(
    (
        'bmgr',
        'gen-bmgr-config',
    )
)

BUILD_REQUIRED_TASKS = frozenset(
    (
        'all',
        'app',
        'app-flash',
        'bootloader',
        'bootloader-flash',
        'build',
        'coredump-debug',
        'coredump-info',
        'diag',
        'encrypted-app-flash',
        'encrypted-flash',
        'flash',
        'gdb',
        'gdbgui',
        'gdbstub',
        'gdbtui',
        'merge-bin',
        'openocd',
        'size',
        'size-components',
        'size-files',
        'uf2',
        'uf2-app',
    )
)

CONFIGURE_PRECHECK_TASKS = frozenset(
    (
        'partition-table',
        'partition-table-flash',
        'reconfigure',
        'refresh-config',
        'save-defconfig',
    )
)

CONFIGURE_BOOTSTRAP_ONLY_TASKS = frozenset(
    (
        'confserver',
        'config-report',
        'menuconfig',
        'set-target',
    )
)

NO_PROJECT_SIDE_EFFECT_TASKS = frozenset(
    (
        'add-dependency',
        'build-system-targets',
        'clean',
        'clang-check',
        'clang-html-report',
        'create-component',
        'create-manifest',
        'create-project',
        'create-project-from-example',
        'dfu-list',
        'docs',
        'efuse-burn',
        'efuse-burn-key',
        'efuse-common-table',
        'efuse-custom-table',
        'efuse-dump',
        'efuse-read-protect',
        'efuse-summary',
        'efuse-write-protect',
        'erase-flash',
        'erase-otadata',
        'fullclean',
        'help',
        'list-targets',
        'mcp-server',
        'monitor',
        'post-debug',
        'python-clean',
        'qemu',
        'read-otadata',
        'remove-dependency',
        'sbom-check',
        'sbom-create',
        'secure-decrypt-flash-data',
        'secure-digest-secure-bootloader',
        'secure-encrypt-flash-data',
        'secure-encrypt-nvs-partition',
        'secure-generate-flash-encryption-key',
        'secure-generate-key-digest',
        'secure-generate-nvs-partition-key',
        'secure-generate-signing-key',
        'secure-sign-data',
        'secure-verify-signature',
        'show-efuse-table',
        'update-dependencies',
    )
)


def _task_candidates(task: object) -> Tuple[str, ...]:
    aliases = getattr(task, 'aliases', None) or ()
    return (getattr(task, 'name', ''),) + tuple(aliases)


def task_names(tasks: Sequence[object]) -> Tuple[str, ...]:
    return tuple(getattr(task, 'name', '') for task in tasks)


def any_task_matches(tasks: Sequence[object], expected_names: Iterable[str]) -> bool:
    expected = frozenset(expected_names)
    for task in tasks:
        for candidate in _task_candidates(task):
            if candidate in expected:
                return True
    return False


def is_build_like(tasks: Sequence[object]) -> bool:
    return any_task_matches(tasks, BUILD_REQUIRED_TASKS)


def is_bmgr_command(tasks: Sequence[object]) -> bool:
    return any_task_matches(tasks, BMGR_COMMAND_TASKS)


def has_only_no_project_side_effect_tasks(tasks: Sequence[object]) -> bool:
    names = task_names(tasks)
    return bool(names) and all(name in NO_PROJECT_SIDE_EFFECT_TASKS for name in names)
