Board Source Directories and Scan Paths
========================================

:link_to_translation:`zh_CN:[中文]`

Before generating code, ``idf.py bmgr`` aggregates the boards available to the current project from the following sources.

Automatic Scan Sources
----------------------

By default, BMGR scans in the following order. **A board with the same name as one already found is skipped**:

1. **BMGR built-in boards/ directory** (``esp_board_manager/boards/``): The default source for official boards in the current version (0.5.x), shipped with the BMGR component and requiring no additional dependency declarations. Starting from 0.6, built-in boards will be fully migrated to independent components.
2. **Project components/ directory** (``components/``): Board components maintained independently within the project, for example ``components/my_board/``, with up to 3 levels of recursion. Suitable for custom boards or modified copies of official boards (board names must differ from built-in boards; if they match, the built-in version takes priority).
3. **Components under ``managed_components/`` with names containing** ``boards``: Board collections downloaded via the component manager, for example ``espressif__esp_boards/``, with up to 3 levels of recursion.
4. **Dependencies with ``path:`` overrides in ``main/idf_component.yml``**: Board dependencies pointed to local directories via ``path:`` in the main component manifest, with up to 3 levels of recursion; commonly used for local debugging.
5. **Board root directory specified by** ``-c`` (``-c <path>``): An additional board collection root directory passed on the command line, with up to 3 levels of recursion. Scanned last; a same-named board from any of the first four sources takes priority.

.. note::

   Recursive N levels deep: starting from the given root directory, at most N levels of subdirectories are expanded; directories beyond that are not traversed.

Run ``idf.py bmgr -l`` to list all boards recognized in the current project along with their source labels.

Selecting a Board by Name: ``-b <name>``
-----------------------------------------

When a board name is passed to ``-b``, BMGR first aggregates the scan pool in the order described above, then searches it for a match:

.. code-block:: bash

   idf.py bmgr -b esp32_s3_korvo2_v3

If the same board name exists in multiple sources, scan order determines priority (the first match takes effect). ``-b`` also accepts an index number corresponding to the order shown by ``idf.py bmgr -l``.

Specifying a Board by Path: ``-b <path>``
------------------------------------------

If the value of ``-b`` is a board directory that exists on disk (absolute path or path relative to the project root), BMGR uses that directory directly and overrides any existing entry with the same name in the scan pool; this takes priority over all automatic scan sources:

.. code-block:: bash

   idf.py bmgr -b /abs/path/to/my_board

Suitable for temporary verification, pointing to a repository path in CI, or debugging an external directory without copying the board into the project.

Combining ``-c`` and ``-b``
----------------------------

``-c <path>`` adds the specified directory to the scan pool (source 5). Typical combinations:

**Selecting a board by name from a custom directory**: If the target board exists only in the ``-c`` path, it can be selected by name from the expanded scan pool:

.. code-block:: bash

   idf.py bmgr -b my_custom_board -c /path/to/custom_boards

**Path selection with extended scan**: When ``-b`` points to a path, the selected board is already determined; other boards in the ``-c`` path are still added to the Kconfig option list and do not affect the currently selected board:

.. code-block:: bash

   idf.py bmgr -b /abs/path/to/my_board -c /path/to/other_boards

Version Notes
-------------

- **Current (0.5.x)**: Official boards are built into the BMGR component (source 1) and are available without declaring additional dependencies.
- **From 0.6 onwards**: Official boards are removed from the BMGR component and split into multiple independent components:

  - BMGR 0.6 declares an ``espressif/esp_boards`` dependency by default in its own ``idf_component.yml``; importing BMGR gives direct access to its boards without additional project configuration.
  - Other board components (such as ``espressif/esp_friends_boards`` and ``espressif/m5stack_boards``) must be manually declared as dependencies in the project's main component manifest (``idf_component.yml``); once downloaded, they are automatically recognized via source 3.

  .. note::

     Some boards currently built into ``esp_board_manager/boards/`` will be migrated to ``espressif/esp_friends_boards`` or ``espressif/m5stack_boards``; after migration they will no longer be available by default and will require manual dependency declarations. For the component each board belongs to, see :doc:`/references/boards/index`.

Recommended Practices
----------------------

- **Using official boards**: In 0.5.x, importing BMGR automatically includes all built-in boards. In 0.6+, importing BMGR automatically includes ``espressif/esp_boards``; if the target board is in another board component, manually declare the corresponding dependency in the project's main component manifest; see :doc:`/references/boards/index` for the component each board belongs to.
- **Custom boards**: Place in the project's ``components/<board_name>/``; avoid names that conflict with built-in official boards. Running ``idf.py bmgr -x`` to clean generated code does not affect this directory.
- **Temporary debugging**: Use ``idf.py bmgr -b /abs/path/to/board``; no need to copy the board into the project.
- **Publishing a board component**: Publish the board directory as a standalone component for easy reference by other projects.
