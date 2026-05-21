使用 -a/--amend
==========================================================================

:link_to_translation:`en:[English]`

在已有开发板上做少量差异（例如修改某个引脚、替换触摸芯片）或是需要追加开发板默认未包含的设备时，无需复制整份开发板目录。准备一个 **amend 目录**，其中放置一份 ``board_amend.yaml`` 清单，再通过 ``-a/--amend <dir>`` 在生成时将变更打补丁到已选开发板之上：

.. code-block:: bash

   # amend 目录是绝对路径或相对路径，其中必须包含 board_amend.yaml
   idf.py bmgr -b esp32_s3_korvo2_v3 -a path/to/my_amend

   # amend 目录放在所选开发板目录下时，可直接传入子目录名
   # 例如：boards/esp32_s3_lcd_ev_board/sub_board_800_480_lcd
   idf.py bmgr -b esp32_s3_lcd_ev_board -a sub_board_800_480_lcd

``-a`` 接受绝对路径或相对路径；常规 IDF 工程中相对路径以项目根目录为基准。 **若 amend 目录放在所选开发板目录下，也可以只传入子目录名，BMGR 会在该开发板目录内查找对应子目录。**

同一主板的不同子板、屏幕模组或小范围硬件变体，建议统一放在该板子目录下（例如 ``boards/esp32_s3_lcd_ev_board/sub_board_800_480_lcd/``），使用时只传入子目录名，不受工程所在路径的影响。

amend 目录的基本结构：

.. code-block:: text

   my_amend/
     board_amend.yaml          # 必需：清单文件
     tweak.yaml                # YAML 片段，需在 apply: 中列出
     extra_setup.c             # 可选源码，需在 apply: 中列出
     sdkconfig.defaults.board  # 可选，需在 apply: 中列出

清单文件
--------------

``board_amend.yaml`` 格式：

.. code-block:: yaml

   version: "1.0"
   description: "Add external sensor power control"

   apply:                        # 有序列表，后者覆盖前者
     - tweak.yaml
     - extra_setup.c
     - sdkconfig.defaults.board

amend 根下的文件（包括 ``sdkconfig.defaults.board``、``Kconfig.projbuild``）\ **必须显式列在 apply: 中才会生效**。仅放置但未列出的文件会被忽略并输出 info 日志。目录项不被支持，子目录下的文件需写出完整的相对路径，例如 ``pack/extra.yaml``。

``apply:`` 中每一项支持的路径写法：

- **相对路径**：相对 ``board_amend.yaml`` 所在目录解析，例如 ``tweak.yaml``、``pack/extra.yaml``、``../shared/extra_setup.c``。
- **绝对路径**：直接使用，例如 ``/abs/path/to/extra_setup.c``。

无论哪种写法，均不支持目录项。子目录下的文件必须按文件名完整展开列出（``pack/extra.yaml``，而非 ``pack``）。

YAML 片段合并规则
----------------------

每个 YAML 片段顶层必须包含 ``devices:`` 或 ``peripherals:``。合并按 ``apply:`` 顺序进行，同名 device 或 peripheral 做字段级合并（``config`` 采用深度合并），不存在的名称追加到列表末尾。

.. code-block:: yaml

   # tweak.yaml 示例：新增一个外设和对应电源控制设备
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

源码文件覆盖
--------------

``apply:`` 中的 ``.c``、``.cpp``、``.cc``、``.cxx``、``.S`` 文件会编译进生成组件。生成组件设置了 ``WHOLE_ARCHIVE``，因此 amend 提供的强符号会覆盖 base 开发板中同名的弱符号函数。典型用法是重写 ``setup_device.c`` 中的初始化钩子。建议基础开发板（base）的钩子函数统一采用 ``__attribute__((weak))`` 与 ``__has_include`` 组合写法，便于 amend 替换，详见 :doc:`/programming-guide/board-directory` 的 ``setup_device.c`` 一节。

跨板复用功能模块
------------------

``apply:`` 支持相对路径，以 ``board_amend.yaml`` 所在目录为基准，可以跳出 amend 目录引用工程其他位置的文件。利用这个特性，可以将通用的外设和设备配置拆成独立的 YAML 与源码片段，集中存放在共享目录下，再由不同开发板的 amend 按需引用——相当于用可复用的功能模块拼装出完整的板级配置。

例如将气体传感器的适配拆成独立片段，放在工程共享目录：

.. code-block:: text

   sensors/
     gas_sensor/
       gas_sensor.yaml   # 外设与设备声明
       gas_sensor.c      # 初始化实现（可选）

某块开发板的 ``board_amend.yaml`` 通过相对路径引用：

.. code-block:: yaml

   version: "1.0"
   description: "Board A: base board + gas sensor"

   apply:
     - ../sensors/gas_sensor/gas_sensor.yaml
     - ../sensors/gas_sensor/gas_sensor.c

需要相同传感器的另一块开发板，直接复用同一批文件，无需重新维护：

.. code-block:: yaml

   version: "1.0"
   description: "Board B: base board + gas sensor + extra periph"

   apply:
     - ../sensors/gas_sensor/gas_sensor.yaml
     - ../sensors/gas_sensor/gas_sensor.c
     - extra_periph.yaml   # 本板特有的额外调整

随着共享目录中功能模块的积累，新开发板的适配可以越来越多地依赖已有模块——在 ``apply:`` 中组合所需片段，而非从头编写重复的 YAML 内容。
