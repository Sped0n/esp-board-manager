开发板参考
============

:link_to_translation:`en:[English]`

开发板参考收纳每块开发板的板级信息：开发板简介、对应芯片、已支持的 device 与 peripheral、是否需要 ``setup_device.c``，以及板级特殊注意事项。

每块开发板的详细页将随开发板组件分批整理。

**当前版本（0.5.x）**：官方开发板随 BMGR 组件一同发布（``esp_board_manager/boards/``），引入 BMGR 即可直接使用，无需额外声明依赖。

**自 BMGR 0.6 起**：开发板从 BMGR 组件内移除，按系列拆分为多个独立板级组件分发：

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - 组件
     - 说明
   * - ``espressif/esp_boards``
     - 乐鑫官方开发板。BMGR 0.6 默认声明此依赖，引入 BMGR 即自动可用，无需工程额外配置。`在线查阅 <https://github.com/espressif/esp-board-manager/tree/main/esp_boards>`__
   * - ``espressif/esp_friends_boards``
     - 合作伙伴与社区开发板。需在工程主组件清单（``idf_component.yml``）中手动声明依赖。`在线查阅 <https://github.com/espressif/esp-board-manager/tree/main/esp_friends_boards>`__
   * - ``espressif/m5stack_boards``
     - M5Stack 系列开发板。需在工程主组件清单中手动声明依赖。`在线查阅 <https://github.com/espressif/esp-board-manager/tree/main/m5stack_boards>`__
