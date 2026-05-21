Create a Board Manually
========================

:link_to_translation:`zh_CN:[中文]`

When no sufficiently similar reference board is available to copy, creating a board manually offers the most flexibility: **create the board directory and three required files, then copy the relevant YAML blocks from the reference pages in this guide for each required device type, and update pin numbers and parameters to match the schematic**.

Steps
-----

**Step 1: Create the Board Directory**

Create a directory named after the board under the project's ``components/`` folder:

.. code-block:: bash

   mkdir -p components/my_board

The directory name is the board name. Only lowercase letters, digits, and underscores are allowed; hyphens are not supported.

**Step 2: Create board_info.yaml**

Create ``components/my_board/board_info.yaml`` and fill in the board-level metadata:

.. code-block:: yaml

   board: my_board          # must match the directory name
   chip: esp32s3            # SoC model (esp32 / esp32s2 / esp32s3 / esp32c3, etc.)
   version: "1.0.0"
   description: "My custom board"
   manufacturer: "MyCompany"

**Step 3: Consult the Reference Pages and Copy Configuration Blocks**

Based on the hardware components on the board schematic, find the corresponding device type page in :doc:`/references/devices/index`. Each page provides a ready-to-copy YAML example in its "Minimal Configuration" section.

Append the ``board_peripherals.yaml`` code block from the reference page to your local ``components/my_board/board_peripherals.yaml``, and append the ``board_devices.yaml`` code block to ``components/my_board/board_devices.yaml``. Each file starts with its respective top-level key (``peripherals:`` or ``devices:``), which should appear only once:

.. code-block:: yaml

   # board_peripherals.yaml example structure
   peripherals:
     - name: i2c_main         # peripheral block copied from the reference page
       type: i2c
       ...
     - name: i2s_audio_out    # append another peripheral block
       type: i2s
       ...

.. code-block:: yaml

   # board_devices.yaml example structure
   devices:
     - name: audio_codec_0    # device block copied from the reference page
       type: audio_codec
       ...

**Step 4: Replace Hardware-Specific Values**

The copied YAML blocks contain two types of markers that must all be resolved before the board can be used (see :doc:`/programming-guide/yaml-rules`):

- ``[IO]``: Corresponds to actual hardware pins. Must be filled in from the schematic; the placeholder value (typically ``-1``) cannot remain.
- ``[TO_BE_CONFIRMED]``: Placeholder or generic default value. Must be confirmed and replaced by consulting the component datasheet.

**Step 5: Add Optional Files as Needed**

.. code-block:: text

   my_board/
     sdkconfig.defaults.board  # board-level sdkconfig defaults
     setup_device.c            # initialization logic that cannot be expressed in YAML
     Kconfig.projbuild         # board-level Kconfig symbol extensions
     packages/                 # board-local components

For the purpose and usage of each optional file, see :doc:`/programming-guide/board-directory`.

**Step 6: Verify**

.. code-block:: bash

   idf.py bmgr -b my_board

After a successful run, ``components/gen_bmgr_codes/`` should contain: ``gen_board_periph_config.c``, ``gen_board_device_config.c``, ``gen_board_info.c``, ``board_manager.defaults``, ``Kconfig.projbuild``, ``idf_component.yml``, and related files.

Before using the board in production, verify the following:

- The board name in ``board_info.yaml`` matches the directory name.
- All ``[IO]`` fields have been filled in from the schematic.
- All ``[TO_BE_CONFIRMED]`` fields have been replaced with actual values.
- All peripheral names referenced by devices exist in ``board_peripherals.yaml``.
- All components listed in ``dependencies`` can be resolved.
- Devices requiring special initialization sequences (LCD display, touchscreen, camera, etc.) have been assessed to determine whether ``setup_device.c`` is needed.

After passing the checks above, run an example or test app on the new board to further verify that peripheral and device initialization works correctly:

- **Examples**: ``esp_board_manager/examples/`` provides audio playback, recording, and LVGL display examples that can be run directly on the new board to validate actual hardware behavior.
- **Test app**: ``esp_board_manager/test_apps/`` provides system-level tests covering the board initialization flow, suitable for comprehensive validation of the generated code.
