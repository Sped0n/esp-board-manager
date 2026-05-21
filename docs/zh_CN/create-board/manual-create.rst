手动创建
==========================================================================

:link_to_translation:`en:[English]`

没有可直接复制的近似参考板时，手动创建是最灵活的方式： **建立板目录和三个必需文件，然后按所需设备类型从参考手册的配置示例中复制对应 YAML 块，并按原理图修改引脚和参数**。

步骤
--------------

**第一步：创建开发板目录**

在工程的 ``components/`` 下创建以开发板名称命名的目录：

.. code-block:: bash

   mkdir -p components/my_board

目录名即开发板名称，只允许小写字母、数字和下划线，不支持中划线。

**第二步：创建 board_info.yaml**

新建 ``components/my_board/board_info.yaml``，填写板级元数据：

.. code-block:: yaml

   board: my_board          # 必须与目录名一致
   chip: esp32s3            # SoC 型号（esp32 / esp32s2 / esp32s3 / esp32c3 等）
   version: "1.0.0"
   description: "My custom board"
   manufacturer: "MyCompany"

**第三步：按需查阅参考手册，复制配置块**

根据开发板原理图上的硬件组成，在 :doc:`/references/devices/index` 中找到对应的设备类型页面，每个页面的"最小配置"节均提供了可直接复制的 YAML 示例。

将参考页中的 ``board_peripherals.yaml`` 代码块内容追加到本地 ``components/my_board/board_peripherals.yaml``，将 ``board_devices.yaml`` 代码块内容追加到 ``components/my_board/board_devices.yaml``。文件分别以 ``peripherals:`` 和 ``devices:`` 开头，顶层键只需出现一次：

.. code-block:: yaml

   # board_peripherals.yaml 示例结构
   peripherals:
     - name: i2c_main         # 从参考页复制的外设块
       type: i2c
       ...
     - name: i2s_audio_out    # 再追加一个外设块
       type: i2s
       ...

.. code-block:: yaml

   # board_devices.yaml 示例结构
   devices:
     - name: audio_codec_0    # 从参考页复制的设备块
       type: audio_codec
       ...

**第四步：替换硬件相关值**

复制后的 YAML 块中包含两类标记，必须全部处理后才能正式使用（详见 :doc:`/programming-guide/yaml-rules`）：

- ``[IO]``：对应真实硬件引脚，必须按原理图填写，不能保留默认占位值（通常为 ``-1``）。
- ``[TO_BE_CONFIRMED]``：占位值或通用默认值，需逐项查阅器件手册确认并替换。

**第五步：按需添加可选文件**

.. code-block:: text

   my_board/
     sdkconfig.defaults.board  # 板级 sdkconfig 默认项
     setup_device.c            # 纯 YAML 无法描述的初始化逻辑
     Kconfig.projbuild         # 板级 Kconfig 符号扩展
     packages/                 # 板级本地组件

各可选文件的用途与写法见 :doc:`/programming-guide/board-directory`。

**第六步：验证**

.. code-block:: bash

   idf.py bmgr -b my_board

生成成功后，``components/gen_bmgr_codes/`` 下应包含：``gen_board_periph_config.c``、``gen_board_device_config.c``、``gen_board_info.c``、``board_manager.defaults``、``Kconfig.projbuild``、``idf_component.yml`` 等文件。

正式使用前逐项确认：

- ``board_info.yaml`` 中的开发板名称与目录名一致。
- 所有 ``[IO]`` 字段已按原理图核实。
- 所有 ``[TO_BE_CONFIRMED]`` 字段已填写真实值。
- 设备引用的所有外设名均存在于 ``board_peripherals.yaml`` 中。
- ``dependencies`` 中的组件能正常解析。
- LCD 显示屏、触摸屏、摄像头等需要特殊时序的设备已确认是否需要 ``setup_device.c``。

通过上述检查后，建议在新开发板上运行示例工程或测试应用，进一步验证外设与设备初始化是否正常：

- **示例工程**：``esp_board_manager/examples/`` 目录下提供了音频播放、录音、LVGL 显示等场景示例，可直接切换至新开发板运行，验证实际硬件行为。
- **测试应用**：``esp_board_manager/test_apps/`` 提供了针对板级初始化流程的系统测试，适合全面验证生成代码的正确性。
