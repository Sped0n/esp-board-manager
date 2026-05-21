Version Migration
==================

:link_to_translation:`zh_CN:[中文]`

This page describes the migration steps and key checkpoints after upgrading BMGR or ESP-IDF, so that users can quickly locate what needs attention beyond the changelog.

Planned topics:

- Version migration involves three categories of change: ESP-IDF version changes, BMGR runtime API or generation logic changes, and YAML schema or field semantic changes.
- Recommend pinning a known-good older version as a baseline.
- Recommended workflow: first read the migration notes and breaking changes, then re-run ``idf.py bmgr -b <board>``, then compare ``gen_bmgr_codes``, ``board_manager.defaults``, and ``Kconfig.projbuild``, and finally perform a full build and minimal runtime regression.
- When upgrading BMGR, pay particular attention to whether command entry points, generated files, macro names, component dependencies, and the default configuration injection method have changed.
- When upgrading ESP-IDF, pay particular attention to whether underlying driver APIs, default configuration items, Kconfig options, component dependencies, and header file paths have changed.
- When the YAML schema is upgraded, provide a side-by-side comparison of old and new usage.
- It is not recommended to copy generated artifacts from an older version directly into a newer version.
- Prepare a version migration checklist.
