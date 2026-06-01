Using -a/--amend
================

:link_to_translation:`zh_CN:[中文]`

When making minor differences on an existing board (such as modifying a pin or replacing a touch chip) or adding devices not included by default, there is no need to copy the entire board directory. Prepare an **amend directory** containing a ``board_amend.yaml`` manifest, then apply changes as patches on top of the selected board during generation using ``-a/--amend <dir>``:

.. code-block:: bash

   # The amend directory is an absolute or relative path and must contain board_amend.yaml
   idf.py bmgr -b esp32_s3_korvo2_v3 -a path/to/my_amend

   # When the amend directory is placed under the selected board directory, pass the subdirectory name directly
   # For example: boards/esp32_s3_lcd_ev_board/sub_board_800_480_lcd
   idf.py bmgr -b esp32_s3_lcd_ev_board -a sub_board_800_480_lcd

``-a`` accepts absolute or relative paths; in a standard IDF project, relative paths are resolved from the project root. **If the amend directory is placed under the selected board directory, only the subdirectory name needs to be passed, and BMGR will look for the corresponding subdirectory inside that board directory.**

Different sub-boards, screen modules, or minor hardware variants of the same main board are recommended to be placed uniformly under that board's subdirectory (for example, ``boards/esp32_s3_lcd_ev_board/sub_board_800_480_lcd/``); only the subdirectory name needs to be passed when using it, and it is not affected by the project path.

Basic structure of the amend directory:

.. code-block:: text

   my_amend/
     board_amend.yaml          # Required: manifest file
     tweak.yaml                # YAML fragment, must be listed under apply:
     extra_setup.c             # Optional source file, must be listed under apply:
     sdkconfig.defaults.board  # Optional, must be listed under apply:

Manifest File
-------------

``board_amend.yaml`` format:

.. code-block:: yaml

   version: "1.0"
   description: "Add external sensor power control"

   apply:                        # Ordered list; later entries override earlier ones
     - tweak.yaml
     - extra_setup.c
     - sdkconfig.defaults.board

Files at the amend root (including ``sdkconfig.defaults.board`` and ``Kconfig.projbuild``) **must be explicitly listed in** ``apply:`` **to take effect**. Files that are placed but not listed will be ignored and an info log will be output. Directory entries are not supported; files in subdirectories must be listed with their full relative paths, such as ``pack/extra.yaml``.

Supported path formats for each entry in ``apply:``:

- **Relative path**: Resolved relative to the directory containing ``board_amend.yaml``, for example ``tweak.yaml``, ``pack/extra.yaml``, ``../shared/extra_setup.c``.
- **Absolute path**: Used directly, for example ``/abs/path/to/extra_setup.c``.

Regardless of the format, directory entries are not supported. Files in subdirectories must be listed with their full filenames expanded (``pack/extra.yaml``, not ``pack``).

YAML Fragment Merge Rules
-------------------------

Each YAML fragment must contain ``devices:`` or ``peripherals:`` at the top level. Merging is performed in the order of ``apply:``. Devices or peripherals with the same name undergo field-level merging (``config`` uses deep merge); names that do not exist are appended to the end of the list.

.. code-block:: yaml

   # Example tweak.yaml: add a peripheral and the corresponding power control device
   peripherals:
     - name: gpio_sensor_power
       type: gpio
       role: io
       version: default
       config:
         pin: 4                  # [IO]
         mode: GPIO_MODE_OUTPUT

   devices:
     - name: sensor_power
       type: power_ctrl
       sub_type: gpio
       version: default
       peripherals:
         - name: gpio_sensor_power
           active_level: 1

Source File Override
--------------------

``.c``, ``.cpp``, ``.cc``, ``.cxx``, and ``.S`` files listed in ``apply:`` are compiled into the generated component. The generated component sets ``WHOLE_ARCHIVE``, so strong symbols provided by the amend override weak symbol functions of the same name in the base board. The typical usage is to rewrite initialization hooks in ``setup_device.c``. It is recommended that hook functions in the base board uniformly use the ``__attribute__((weak))`` and ``__has_include`` combination to facilitate amend replacement; see the ``setup_device.c`` section in :doc:`/programming-guide/board-directory`.

Cross-Board Module Reuse
------------------------

``apply:`` supports relative paths, resolved from the directory containing ``board_amend.yaml``, allowing references to files outside the amend directory at other locations in the project. Using this feature, common peripheral and device configurations can be split into independent YAML and source code fragments, stored centrally in a shared directory, and then referenced on demand by different boards' amend files—effectively assembling a complete board-level configuration from reusable feature modules.

For example, to split the gas sensor adaptation into an independent fragment and place it in the project shared directory:

.. code-block:: text

   sensors/
     gas_sensor/
       gas_sensor.yaml   # Peripheral and device declarations
       gas_sensor.c      # Initialization implementation (optional)

A board's ``board_amend.yaml`` references it via a relative path:

.. code-block:: yaml

   version: "1.0"
   description: "Board A: base board + gas sensor"

   apply:
     - ../sensors/gas_sensor/gas_sensor.yaml
     - ../sensors/gas_sensor/gas_sensor.c

Another board that needs the same sensor directly reuses the same files without needing to maintain them again:

.. code-block:: yaml

   version: "1.0"
   description: "Board B: base board + gas sensor + extra periph"

   apply:
     - ../sensors/gas_sensor/gas_sensor.yaml
     - ../sensors/gas_sensor/gas_sensor.c
     - extra_periph.yaml   # Board-specific additional tweaks

As feature modules accumulate in the shared directory, adapting new boards can rely increasingly on existing modules—combining the required fragments in ``apply:`` rather than writing repetitive YAML content from scratch.
