代码生成与构建集成
==========================================================================

:link_to_translation:`en:[English]`

BMGR 在编译前先将开发板的 YAML 描述解析为一组明确的配置源码和构建输入，``idf.py bmgr`` 是面向用户的入口命令。

执行 ``idf.py bmgr -b <board>`` 时，BMGR 依次完成以下工作：

1. 扫描开发板目录，收集默认目录、自定义目录和组件目录中的候选开发板。
2. 根据命令行参数（名称或索引）确定当前选中的开发板。
3. 定位该开发板对应的 ``board_peripherals.yaml``、``board_devices.yaml``、``board_info.yaml``、``sdkconfig.defaults.board``、``Kconfig.projbuild``。
4. 解析外设和设备，生成对应的配置结构、句柄表和板级元数据。
5. 生成当前开发板相关的 ``Kconfig.projbuild``，追加板级目录下的 ``Kconfig.projbuild``。
6. 生成 ``board_manager.defaults``，将板级默认配置和当前开发板的能力符号接入构建。
7. 在 ``components/gen_bmgr_codes`` 下输出参与编译的源码、构建文件和工具摘要文件。

在 BMGR 的模型中，开发板的配置代码来自 YAML 文件描述以及脚本的解析与生成流程，而非通过 ``menuconfig`` 手动勾选设备或外设。``components/gen_bmgr_codes`` 不是缓存，也不是仅供查看的中间产物，而是会参与 ESP-IDF 构建的实际组件。

生成产物说明
----------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - 文件
     - 说明
   * - ``gen_board_periph_config.c``
     - 基于 ``board_peripherals.yaml`` 生成的外设配置结构体定义。
   * - ``gen_board_periph_handles.c``
     - 生成的 peripheral 句柄入口、类型映射和初始化函数挂接点。
   * - ``gen_board_device_config.c``
     - 基于 ``board_devices.yaml`` 生成的 device 配置结构体定义。
   * - ``gen_board_device_handles.c``
     - 生成的 device 句柄入口、初始化/反初始化函数映射和设备链表。
   * - ``gen_board_info.c``
     - 生成的板级元数据，例如板名、芯片、版本、描述和厂商。
   * - ``gen_board_device_custom.h``
     - ``type: custom`` 设备的配置 struct 定义，供应用侧 ``init`` / ``deinit`` 使用。
   * - ``board_manager.defaults``
     - 当前板配置的 ``sdkconfig`` 默认项，以及对应的设备/外设能力符号。
   * - ``Kconfig.projbuild``
     - 当前板相关的 Kconfig 符号定义和选择入口，把板级能力投射进工程侧配置系统。
   * - ``idf_component.yml``
     - 当前板对应的组件依赖描述，设备 ``dependencies`` 反映到这里。
   * - ``gen_board_metadata.yaml``
     - 面向工具和排查的统一板级摘要，便于查看当前板有哪些设备、外设、组件依赖和占用 IO。

BMGR 不通过在 ``menuconfig`` 中逐项手动选择设备或外设来组织编译，而是先根据板级 YAML 生成 ``board_manager.defaults``，其中包含的板级能力宏在后续构建过程中生效。执行 ``idf.py`` 命令时，BMGR 将这些配置注入 ``sdkconfig``，驱动 BMGR 的条件编译。

排查时建议按现象分流：

- 当表现为功能与预期不一致时，优先检查 ``gen_board_periph_config.c`` 与 ``gen_board_device_config.c``。
- 当表现为编译失败或依赖求解异常时，优先检查 ``components/gen_bmgr_codes`` 目录下生成物是否完整、``board_manager.defaults`` 中的能力符号是否符合预期，以及 ``sdkconfig`` 与 ``board_manager.defaults`` 是否一致。
