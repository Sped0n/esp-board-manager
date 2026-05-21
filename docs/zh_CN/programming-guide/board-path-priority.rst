开发板来源与扫描路径
==========================================================================

:link_to_translation:`en:[English]`

``idf.py bmgr`` 在生成代码前，从以下来源汇总当前工程可用的开发板。

自动扫描来源
--------------

BMGR 默认按如下顺序扫描，\ **同名开发板以先扫描到的为准，后来者被跳过**\ ：

1. **BMGR 内置 boards/ 目录**\ （``esp_board_manager/boards/``）：当前版本（0.5.x）官方开发板的默认来源，随 BMGR 组件一同发布，无需额外声明依赖。自 0.6 起内置开发板将全部迁移至独立组件。
2. **工程 components/ 目录**\ （``components/``）：工程内独立维护的开发板组件，例如 ``components/my_board/``，最多向下递归 3 层。适合存放自定义开发板或对官方开发板做改动后的副本（开发板名称须与内置板不同，否则内置版本优先）。
3. **managed_components/ 下名称含 boards 的组件**：通过组件管理器下载的开发板集合，例如 ``espressif__esp_boards/``，最多向下递归 3 层。
4. **main/idf_component.yml 中 path 覆盖的依赖**：在主组件清单中通过 ``path:`` 将某个 board 依赖指向本地目录，最多向下递归 3 层，常用于本地调试。
5. **-c 指定的板根目录**\ （``-c <path>``）：通过命令行传入的附加板集合根目录，最多向下递归 3 层。扫描顺序最后，同名时被前四个来源覆盖。

.. note::

   向下递归 N 层：从给定根目录出发，最多展开 N 层子目录，超出部分不再展开。

执行 ``idf.py bmgr -l`` 可列出当前工程识别到的全部开发板及其来源标记。

按名称选板：``-b <name>``
-----------------------------

``-b`` 传入开发板名称时，BMGR 先按上述顺序汇总扫描池，再从中查找匹配项：

.. code-block:: bash

   idf.py bmgr -b esp32_s3_korvo2_v3

若多个来源存在同名开发板，扫描顺序即为优先级（先扫描到的生效）。``-b`` 也接受序号，序号与 ``idf.py bmgr -l`` 输出的顺序对应。

直接指定路径：``-b <path>``
-------------------------------

若 ``-b`` 的值是磁盘上已存在的开发板目录（绝对路径，或相对工程根的路径），BMGR 直接使用该目录，并覆盖扫描池中同名的已有条目，优先级高于所有自动扫描来源：

.. code-block:: bash

   idf.py bmgr -b /abs/path/to/my_board

适用于临时验证、CI 中指向代码仓库路径，或调试外部目录而无需将开发板复制进工程。

``-c`` 与 ``-b`` 组合
------------------------

``-c <path>`` 将指定目录加入扫描池（第 5 来源）。典型组合：

**按名称从自定义目录选板**：若目标开发板仅存在于 ``-c`` 路径，可在扩展后的扫描池中直接按名称选中：

.. code-block:: bash

   idf.py bmgr -b my_custom_board -c /path/to/custom_boards

**路径 + 扩展扫描**：``-b`` 指向路径时所选开发板已确定，``-c`` 路径中的其他开发板仍会加入 Kconfig 选项列表，不影响当前选中的开发板：

.. code-block:: bash

   idf.py bmgr -b /abs/path/to/my_board -c /path/to/other_boards

版本说明
----------

- **当前（0.5.x）**：官方开发板内置于 BMGR 组件（来源 1），无需额外声明依赖即可使用。
- **自 0.6 起**：官方开发板从 BMGR 组件内移除，拆分为多个独立组件：

  - BMGR 0.6 在其自身的 ``idf_component.yml`` 中默认声明 ``espressif/esp_boards`` 依赖，引入 BMGR 即可直接访问其中的开发板，工程无需额外配置。
  - 其他板级组件（如 ``espressif/esp_friends_boards``、 ``espressif/m5stack_boards``）需要在工程主组件清单（``idf_component.yml``）中手动声明依赖，下载后通过来源 3 自动识别。

  .. note::

     当前内置于 ``esp_board_manager/boards/`` 的部分开发板将迁移至 ``espressif/esp_friends_boards`` 或 ``espressif/m5stack_boards``，迁移后不再默认可用，需手动声明对应依赖。各开发板所属组件，参见 :doc:`/references/boards/index`。

推荐做法
----------

- **使用官方开发板**：0.5.x 引入 BMGR 即自动包含所有内置开发板。0.6+ 引入 BMGR 即自动包含 ``espressif/esp_boards``；若目标开发板位于其他板级组件，在工程主组件清单中手动声明对应依赖，各开发板所属组件见 :doc:`/references/boards/index`。
- **自定义开发板**：放在工程 ``components/<board_name>/``，名称避免与内置官方板重名。``idf.py bmgr -x`` 清理生成代码时不会影响该目录。
- **临时调试**：``idf.py bmgr -b /abs/path/to/board``，无需将开发板复制进工程。
- **发布板级组件**：将开发板目录发布为独立组件，方便其他工程引用。
