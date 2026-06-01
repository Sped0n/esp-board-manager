使用 idf.py bmgr -n
==========================================================================

:link_to_translation:`en:[English]`

``idf.py bmgr -n`` 通过交互式选择芯片、设备和外设生成带完整注释的 YAML 模板文件，适合首次适配、不熟悉各字段默认值的场景。模板生成后仍需人工填写硬件引脚和参数，不能直接使用。

.. only:: html

    .. figure:: ../../_static/create-board/how_to_customize_board.gif
        :align: center
        :alt: 使用 idf.py bmgr -n 创建开发板模板示例

.. only:: latex

    `使用 idf.py bmgr -n 创建开发板模板示例 <https://dl.espressif.com/public/how_to_customize_board.gif>`__

生成模板
--------------

``-n`` 参数接受开发板名称或路径：

.. code-block:: bash

   # 在默认路径创建（{PROJECT_ROOT}/components/<board_name>）
   idf.py bmgr -n my_board

   # 在指定路径创建
   idf.py bmgr -n path/to/boards/my_board

执行后按提示依次选择芯片、设备和外设，脚本会检查设备对外设的依赖关系，并在发现缺漏时提示补充。

填写模板
--------------

生成完成后，模板文件中会有两类标记重点关注，详见 :doc:`/programming-guide/yaml-rules`：

- ``[IO]``：对应真实硬件引脚，必须按实际原理图填写。
- ``[TO_BE_CONFIRMED]``：占位值或通用默认值，必须逐项查阅器件资料确认并替换。

此外还需检查：

- 设备名与外设名在各自文件中无重名。
- 设备引用的 peripheral ``name`` 与 ``board_peripherals.yaml`` 中的名称完全一致。

各文件的完整字段说明见 :doc:`/programming-guide/board-directory`。

验证
--------------

.. code-block:: bash

   # 通过名称匹配
   idf.py bmgr -b my_board

   # 通过自定义板根目录指定来源
   idf.py bmgr -b my_board -c /path/to/boards

   # 直接指向硬盘上的开发板目录
   idf.py bmgr -b /abs/path/to/my_board

生成成功后，``components/gen_bmgr_codes/`` 下应包含：``gen_board_periph_config.c``、``gen_board_device_config.c``、``gen_board_info.c``、``board_manager.defaults``、``Kconfig.projbuild``、``idf_component.yml`` 等文件。

正式使用前逐项确认：

- ``board_info.yaml`` 中的开发板名称与目录名一致。
- 所有 ``[IO]`` 字段已按原理图核实。
- 所有 ``[TO_BE_CONFIRMED]`` 字段已填写真实值。
- 设备引用的所有外设名均存在于 ``board_peripherals.yaml`` 中。
- ``dependencies`` 中的组件能正常解析。
- LCD 显示屏、触摸屏控制器、摄像头等需要特殊时序的设备已确认是否需要 ``setup_device.c``。

通过上述检查后，建议在新开发板上运行示例工程或测试应用，进一步验证外设与设备初始化是否正常：

- **示例工程**：``esp_board_manager/examples/`` 目录下提供了音频播放、录音、LVGL 显示等场景示例，可直接切换至新开发板运行，验证实际硬件行为。
- **测试应用**：``esp_board_manager/test_apps/`` 提供了针对板级初始化流程的系统测试，适合全面验证生成代码的正确性。
