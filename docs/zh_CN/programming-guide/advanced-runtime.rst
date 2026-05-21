进阶运行时能力
==========================================================================

:link_to_translation:`en:[English]`

除"初始化后获取句柄"这条主路径外，BMGR 还提供以下面向进阶场景的运行时能力。

运行时覆盖设备配置
--------------------------

相关接口：

- :cpp:func:`esp_board_device_override_config`
- :cpp:func:`esp_board_device_restore_config`

这组接口在 RAM 中保存一份覆盖后的配置，使后续 ``get_config``、``init``、``callback_register`` 等路径优先使用它。覆盖不会立即改写已经运行中的设备实例，通常需要在 ``init`` 之前调用，或先 ``deinit`` 后再 ``init``，新的配置才会真正作用到驱动。

手动设备电源控制
--------------------------

相关接口：:cpp:func:`esp_board_device_power_ctrl`。

适用于设备存在独立上电或断电动作、且应用需要在 BMGR 自动流程之外显式控制的场景。该接口根据设备描述中的 ``power_ctrl_device`` 找到对应的控制设备，再调用与该 ``sub_type`` 对应的电源控制扩展函数。能否控制以及如何控制，取决于具体 power control device 的实现。当前 power control device 仅支持 GPIO 子类。对于 IO 扩展芯片或电源芯片等较复杂的电源控制设备，可先通过 ``depends_on`` 声明依赖，确保初始化该设备时所需的电源管理设备已被初始化。

设备回调注册
--------------------------

相关接口：:cpp:func:`esp_board_device_callback_register`。

部分设备的正常使用依赖回调函数注册。BMGR 对注册接口做了统一封装，应用层可根据 device type 查找对应的扩展回调注册函数，再传入当前有效配置和运行时句柄。该能力是否可用以及回调签名取决于具体设备的实现，详见各设备参考页。

按名称初始化或反初始化单个设备
------------------------------------

相关接口：

- :cpp:func:`esp_board_manager_init_device_by_name`
- :cpp:func:`esp_board_manager_deinit_device_by_name`

该类接口常与 ``init_skip``、延迟初始化、局部资源回收等场景配合使用。对于需要先完成整板初始化、再按业务时机打开特定设备的工程，比一次性初始化所有设备更灵活。
