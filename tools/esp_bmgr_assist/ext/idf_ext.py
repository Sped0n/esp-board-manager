"""
Legacy path: point ``IDF_EXTRA_ACTIONS_PATH`` at this ``ext/`` directory.

Installations should rely on ``esp_bmgr_py.bmgr_placeholder_ext`` via the injector instead.
"""

from esp_bmgr_py.bmgr_placeholder_ext import action_extensions

__all__ = ['action_extensions']
