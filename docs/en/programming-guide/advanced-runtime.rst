Advanced Runtime Capabilities
==============================

:link_to_translation:`zh_CN:[中文]`

In addition to the primary path of obtaining a handle after initialization, BMGR provides the following runtime capabilities for advanced scenarios.

Runtime Device Configuration Override
--------------------------------------

Related APIs:

- :cpp:func:`esp_board_device_override_config`
- :cpp:func:`esp_board_device_restore_config`

This pair of APIs saves an overridden configuration in RAM so that subsequent ``get_config``, ``init``, and ``callback_register`` paths use it preferentially. The override does not immediately affect a device instance that is already running; it typically needs to be called before ``init``, or after ``deinit`` and before calling ``init`` again, for the new configuration to take effect on the driver.

Manual Device Power Control
----------------------------

Related API: :cpp:func:`esp_board_device_power_ctrl`.

This applies when a device has an independent power-on or power-off action and the application needs to explicitly control it outside the automatic BMGR flow. The API locates the controlling device based on ``power_ctrl_device`` in the device description, then calls the power-control extension function corresponding to that ``sub_type``. Whether and how control is possible depends on the specific power control device implementation. Currently, only the GPIO sub-type is supported for power control devices. For more complex power control devices such as I/O expander chips or power management ICs, you can declare a dependency using ``depends_on`` to ensure the required power management device is initialized before this device.

Device Callback Registration
-----------------------------

Related API: :cpp:func:`esp_board_device_callback_register`.

Some devices require callback registration for normal operation. BMGR provides a unified wrapper for the registration interface; the application can look up the corresponding extension callback registration function by device type, then pass in the current effective configuration and the runtime handle. Whether this capability is available and the callback signature depend on the specific device implementation; see the individual device reference pages for details.

Initialize or Deinitialize a Device by Name
--------------------------------------------

Related APIs:

- :cpp:func:`esp_board_manager_init_device_by_name`
- :cpp:func:`esp_board_manager_deinit_device_by_name`

These APIs are commonly used with ``init_skip``, deferred initialization, and partial resource reclamation scenarios. For projects that need to complete full-board initialization first and then enable specific devices at the appropriate time, they offer more flexibility than initializing all devices at once.
