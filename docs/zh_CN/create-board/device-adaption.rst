开发板设备适配
==============

:link_to_translation:`en:[English]`

板级设备的配置以 BMGR 设备参考页为主要参考来源。本节说明如何利用设备参考文档完成板级配置，以及 BMGR 尚不支持的硬件如何处理。

参照设备参考页配置
---------------------

BMGR 针对每种内置设备类型提供了专属的设备参考页（:doc:`/references/devices/index`），每页包含\ **最小配置**\ 与\ **完整字段**\ 两类模板：

- **最小配置**\ ：按常见接口和 ``sub_type`` 列出的 ``board_peripherals.yaml`` 与 ``board_devices.yaml`` 最小示例，适合直接复制后按原理图修改。
- **完整字段**\ ：包含该设备类型所有可配置字段及取值说明，覆盖 BMGR 解析器支持的所有选项。

即使现有板子中未使用某个配置组合，也可在对应设备页的"完整字段"模板中找到字段注释与取值参考。

建议方式：打开目标设备类型的参考页，从"最小配置"模板中找到与硬件接口一致的示例，按原理图及设备实际情况替换 ``[IO]`` 和 ``[TO_BE_CONFIRMED]`` 字段，根据需要参考"完整字段"调整可选参数。

.. note::

   ``audio_codec`` 设备的 I2S 标准模式麦克风与扬声器是一个典型示例——该配置在现有板子中未被广泛使用，但其字段与用法已在设备参考页中完整记录，可直接参照配置。详见 :doc:`/references/devices/audio-codec`。

使用 custom 设备类型
----------------------

若 BMGR 尚无内置的设备类型与目标硬件对应，可使用 ``custom`` 设备类型实现适配：

1. 在 ``board_devices.yaml`` 中以 ``type: custom`` 声明设备，``name`` 字段按硬件功能命名。
2. BMGR 生成阶段会为该设备生成专属配置结构体 ``dev_custom_{name}_config_t``。
3. 在 ``setup_device.c`` 或其他参与构建的源文件中，通过 ``CUSTOM_DEVICE_IMPLEMENT`` 宏注册 init 与 deinit 实现。
4. 运行时 BMGR 将按设备名称查找并调用注册的实现。

详见 :doc:`/references/devices/custom`。
