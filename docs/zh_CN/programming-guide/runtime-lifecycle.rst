运行时生命周期
==========================================================================

:link_to_translation:`en:[English]`

从运行时角度看，BMGR 固定了一组顺序：先初始化哪些外设、再初始化哪些设备、如何获取对应的句柄与配置。

主入口为 :cpp:func:`esp_board_manager_init`。从源码实现看，该函数先调用 :cpp:func:`esp_board_periph_init_all`，再调用 :cpp:func:`esp_board_device_init_all`。如果设备初始化失败，还会回退并尝试释放已经初始化的外设。对应地，:cpp:func:`esp_board_manager_deinit` 先反初始化所有 device，再反初始化所有 peripheral。

关键行为
--------------

- **外设先初始化，设备后初始化**：设备通常依赖某个外设句柄才能创建实例。调用 :cpp:func:`esp_board_manager_init` 时，BMGR 固定按先外设、后设备的顺序执行。
- **整体遍历顺序与 YAML 书写顺序相关**：:cpp:func:`esp_board_device_init_all` 按 ``board_devices.yaml`` 中的条目顺序遍历设备。声明了 ``depends_on`` 的设备在初始化时会递归先初始化依赖，与 YAML 中条目的前后顺序无关。
- ``depends_on``\ **声明设备间的初始化依赖**：当 device 配置了 ``depends_on`` 时，:cpp:func:`esp_board_device_init` 在初始化该 device 之前会递归先初始化所列依赖设备，无需在 ``board_devices.yaml`` 中手动保证顺序。依赖设备若已由其他路径初始化（``ref_count > 0``），不会重复创建实例。依赖的设备类型不限，一个设备可以声明多个依赖项。
- **反初始化按引用计数收敛**：设备和外设内部均维护引用计数（``ref_count``）。重复初始化同一对象时，不会重复创建实例，而是增加引用计数。计数降至 0 时才真正释放。
- ``init_skip``\ **跳过自动初始化**：带 ``init_skip`` 的 device 仍存在于板级描述和生成结果中，但 :cpp:func:`esp_board_manager_init` 不会主动初始化它，适合需要按业务时机延迟创建的设备。
- ``power_ctrl_device``\ **控制设备上电时序**：当 device 声明了 ``power_ctrl_device`` 时，BMGR 在初始化该 device 之前先通过对应的 ``power_ctrl`` 设备执行上电动作；反初始化时也会触发下电。``power_ctrl_device`` 是专门针对供电控制的设备间引用，被引用的设备类型必须为 ``power_ctrl``。与 ``depends_on`` 相比，``power_ctrl_device`` 额外触发上电与下电动作，并提供运行时的电源控制 API :cpp:func:`esp_board_device_power_ctrl`，作用不局限于保证初始化顺序。
- 结合使用 ``depends_on`` 与 ``power_ctrl_device``，可以保证即使通过 :cpp:func:`esp_board_manager_init_device_by_name` 单独初始化某个设备，也不会因供电或其他依赖问题导致初始化失败。

BMGR 的运行时模型不会将所有初始化逻辑压缩到一次 ``init()`` 调用中，而是按板级描述组织初始化顺序，同时保留引用计数、延迟初始化、设备间依赖和电源控制等运行时行为。
