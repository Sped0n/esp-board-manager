Board Device Adaption
=====================

:link_to_translation:`zh_CN:[中文]`

Board-level device configuration primarily references the BMGR device reference pages. This section explains how to use the device reference documentation for board-level configuration, and how to handle hardware not yet supported by BMGR.

Configure via Device Reference Pages
--------------------------------------

BMGR provides a dedicated device reference page for each built-in device type (:doc:`/references/devices/index`), with each page containing two types of templates: **minimum configuration** and **full fields**:

- **Minimum configuration**: Minimal examples of ``board_peripherals.yaml`` and ``board_devices.yaml`` listed by common interface and ``sub_type``, suitable for copying directly and modifying according to the schematic.
- **Full fields**: Contains all configurable fields and value descriptions for the device type, covering all options supported by the BMGR parser.

Even if a particular configuration combination is not used in existing boards, the field annotations and value references can be found in the "Full Fields" template on the corresponding device page.

Recommended approach: Open the reference page for the target device type, find the example in the "Minimum Configuration" template that matches the hardware interface, replace ``[IO]`` and ``[TO_BE_CONFIRMED]`` fields according to the schematic and actual device, and refer to "Full Fields" to adjust optional parameters as needed.

.. note::

   The I2S standard mode microphone and speaker in the ``audio_codec`` device is a typical example—this configuration is not widely used in existing boards, but its fields and usage are fully documented on the device reference page and can be configured directly. See :doc:`/references/devices/audio-codec`.

Using the custom Device Type
-----------------------------

If BMGR does not yet have a built-in device type corresponding to the target hardware, use the ``custom`` device type for adaptation:

1. Declare the device in ``board_devices.yaml`` with ``type: custom``, with the ``name`` field named according to the hardware function.
2. During the BMGR generation phase, a dedicated configuration structure ``dev_custom_{name}_config_t`` will be generated for this device.
3. In ``setup_device.c`` or other source files participating in the build, register the init and deinit implementations using the ``CUSTOM_DEVICE_IMPLEMENT`` macro.
4. At runtime, BMGR will look up and call the registered implementation by device name.

See :doc:`/references/devices/custom` for details.
