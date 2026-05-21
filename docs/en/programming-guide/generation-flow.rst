Code Generation and Build Integration
======================================

:link_to_translation:`zh_CN:[中文]`

Before compilation, BMGR parses the board's YAML description into a set of explicit configuration source files and build inputs. ``idf.py bmgr`` is the user-facing entry command.

When running ``idf.py bmgr -b <board>``, BMGR performs the following steps in order:

1. Scans board directories, collecting candidate boards from the default directory, custom directory, and component directories.
2. Determines the currently selected board based on the command-line arguments (name or index).
3. Locates the board's ``board_peripherals.yaml``, ``board_devices.yaml``, ``board_info.yaml``, ``sdkconfig.defaults.board``, and ``Kconfig.projbuild``.
4. Parses peripherals and devices, generating corresponding configuration structures, handle tables, and board-level metadata.
5. Generates the ``Kconfig.projbuild`` for the current board and appends the board directory's ``Kconfig.projbuild``.
6. Generates ``board_manager.defaults``, connecting the board's default configuration and capability symbols to the build.
7. Outputs the source files, build files, and tooling summary files under ``components/gen_bmgr_codes`` for compilation.

In BMGR's model, board configuration code comes from the YAML file description and the script's parsing and generation process, not from manually selecting devices or peripherals in ``menuconfig``. ``components/gen_bmgr_codes`` is not a cache or a view-only intermediate artifact; it is an actual component that participates in the ESP-IDF build.

Generated Output Files
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - File
     - Description
   * - ``gen_board_periph_config.c``
     - Peripheral configuration structure definitions generated from ``board_peripherals.yaml``.
   * - ``gen_board_periph_handles.c``
     - Generated peripheral handle entry points, type mappings, and initialization function hooks.
   * - ``gen_board_device_config.c``
     - Device configuration structure definitions generated from ``board_devices.yaml``.
   * - ``gen_board_device_handles.c``
     - Generated device handle entry points, initialization/deinitialization function mappings, and device linked list.
   * - ``gen_board_info.c``
     - Generated board-level metadata, such as board name, chip, version, description, and manufacturer.
   * - ``gen_board_device_custom.h``
     - Configuration struct definitions for ``type: custom`` devices, used by application-side ``init`` and ``deinit``.
   * - ``board_manager.defaults``
     - ``sdkconfig`` default entries for the current board, along with the corresponding device and peripheral capability symbols.
   * - ``Kconfig.projbuild``
     - Kconfig symbol definitions and selection entries for the current board, projecting board-level capabilities into the project configuration system.
   * - ``idf_component.yml``
     - Component dependency manifest for the current board; device ``dependencies`` are reflected here.
   * - ``gen_board_metadata.yaml``
     - A unified board-level summary for tooling and debugging; useful for viewing the devices, peripherals, component dependencies, and occupied I/O of the current board.

BMGR does not organize compilation by manually selecting devices or peripherals one by one in ``menuconfig``; instead, it first generates ``board_manager.defaults`` from the board-level YAML, and the board capability macros contained therein take effect during the subsequent build. When running ``idf.py``, BMGR injects these settings into ``sdkconfig`` to drive BMGR's conditional compilation.

During debugging, it is recommended to triage by symptom:

- If the behavior does not match expectations, check ``gen_board_periph_config.c`` and ``gen_board_device_config.c`` first.
- If the symptom is a build failure or dependency resolution error, check whether the generated files under ``components/gen_bmgr_codes`` are complete, whether the capability symbols in ``board_manager.defaults`` match expectations, and whether ``sdkconfig`` is consistent with ``board_manager.defaults``.
