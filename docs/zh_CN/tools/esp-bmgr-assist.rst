esp-bmgr-assist
========================================

:link_to_translation:`en:[English]`

``esp-bmgr-assist`` 是 BMGR 的 Python 辅助包（源码位于仓库 ``tools/esp_bmgr_assist/``）。它通过 ``.pth`` hook 接入 ``idf.py`` 启动流程，自动发现当前工程使用的 ``esp_board_manager`` 组件并加入 ``IDF_EXTRA_ACTIONS_PATH``，让 ``idf.py bmgr`` 命令直接可用，省去手动配置环境变量。

它不替代 ``esp_board_manager`` 组件，也不生成板级代码：板级代码仍由组件内的 ``gen_bmgr_config_codes.py`` 完成。

安装
------------

请先激活 ESP-IDF 的 Python 环境（在 IDF 目录下 ``./install.sh`` 与 ``. ./export.sh``），再执行：

.. code-block:: bash

   pip install esp-bmgr-assist

升级：

.. code-block:: bash

   pip install --upgrade esp-bmgr-assist

从仓库内本地源码安装：

.. code-block:: bash

   pip install --no-build-isolation ./tools/esp_bmgr_assist

切换到新的 ESP-IDF Python 环境后需要重新安装。

自动发现规则
----------------

``esp-bmgr-assist`` 会按以下顺序在当前工程中查找 ``esp_board_manager`` 组件：

- ``components/esp_board_manager``
- ``components/espressif__esp_board_manager``
- ``managed_components/espressif__esp_board_manager``
- ``idf_component.yml`` 中 ``override_path`` / ``path`` 指向的本地组件
- ``dependencies.lock`` 解析出的 ``esp_board_manager``
- 项目依赖图中直接或间接依赖的 ``espressif/esp_board_manager``

只有同时包含 ``idf_ext.py``、``idf_component.yml`` 和 ``gen_bmgr_config_codes.py`` 的目录才会被识别为有效组件目录。

工程首次执行 ``idf.py bmgr ...`` 而托管组件尚未下载时，辅助工具会触发依赖解析并下载 ``esp_board_manager``，下载完成后再加载 Board Manager action。

构建前预检查
----------------

执行 ``idf.py build`` 一类命令时，``esp-bmgr-assist`` 会先检查：

- ``components/gen_bmgr_codes/*`` 生成物是否缺失。
- ``sdkconfig`` 与 ``gen_bmgr_codes/board_manager.defaults`` 中的 ``CONFIG_IDF_TARGET`` 是否不一致。

默认发现问题就中断命令。通过参数或环境变量调整等级：

.. code-block:: bash

   idf.py --bmgr-preflight-level warning build   # 只输出警告
   idf.py --bmgr-preflight-level silent build    # 跳过

   export ESP_BMGR_ASSIST_PREFLIGHT=warning      # 等效环境变量

支持的等级：``error`` / ``abort``\ （默认）、``warning`` / ``warn``、``silent`` / ``off``。预检查只针对 build 类命令，不会干扰 ``set-target``、``menuconfig``、``confserver`` 等交互或配置命令。

调试与回退
----------------

调试自动发现过程：

.. code-block:: bash

   export ESP_BMGR_DEBUG=1
   idf.py bmgr -l

回退方案：未安装 ``esp-bmgr-assist`` 或自动发现失败时，可以手动设置 ``IDF_EXTRA_ACTIONS_PATH`` 指向 ``esp_board_manager`` 组件目录（多个路径用 ``;`` 分隔，不要用 ``:``）。

已知问题
----------------

间接依赖时回退到 ``esp32`` target
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

如果 ``esp_board_manager`` 通过上游组件间接引入（即 ``main/idf_component.yml`` 未直接声明），辅助工具需要解析完整依赖图，依赖 ``IDF_TARGET`` 才能给出正确结果。读不到时回退到 ``esp32``，可能导致只支持特定 target 的组件依赖解析失败。

处理方式：

1. 执行 ``idf.py set-target <target>`` 拉取 ESP Board Manager 组件。
2. 或在执行 Board Manager 命令时临时指定 target：

.. code-block:: bash

   IDF_TARGET=esp32s3 idf.py bmgr -l
   ESP_BMGR_BOOTSTRAP_TARGET=esp32p4 idf.py bmgr -b <board>

工程在 ``main/idf_component.yml`` 中直接声明 ``espressif/esp_board_manager`` 时走最小化下载路径，通常不受该问题影响。

等待引导锁导致命令疑似卡住
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``esp-bmgr-assist`` 使用项目目录下的 ``.esp_bmgr_py.lock`` 在多个 ``idf.py`` 进程之间序列化引导流程，避免并发触发组件下载。如果同一工程目录下另一个 ``idf.py`` 命令正在引导或下载组件，新的命令会先等待这个锁。

进入等待时会打印一条提示，例如：

.. code-block:: text

   [esp-bmgr-assist] Waiting for board manager bootstrap lock.
   lock: /path/to/project/.esp_bmgr_py.lock
   timeout: 60s
   If this waits unexpectedly, check the process holding the lock:
     lsof /path/to/project/.esp_bmgr_py.lock
     fuser -v /path/to/project/.esp_bmgr_py.lock

默认超时 60 秒，超时后会输出 ``Timed out waiting for board manager bootstrap lock.`` 并中断命令。提示中给出的 ``lsof`` / ``fuser -v`` 适用于 Linux 和 macOS，Windows 用户参考下面的分平台排查方式。

排查步骤：

1. 确认是否有真实的 ``idf.py`` / ``python`` 进程持锁。

   Linux / macOS：

   .. code-block:: bash

      lsof /path/to/project/.esp_bmgr_py.lock
      fuser -v /path/to/project/.esp_bmgr_py.lock

   Windows：使用 Sysinternals 的 ``handle.exe``，或打开任务管理器/资源监视器（``resmon.exe``）的 CPU > 关联的句柄 搜索锁文件名：

   .. code-block:: bat

      handle.exe \path\to\project\.esp_bmgr_py.lock

2. 如果没有进程持锁（例如上一次命令被强杀留下了锁文件），手动删除锁文件后重试：

   Linux / macOS：

   .. code-block:: bash

      rm /path/to/project/.esp_bmgr_py.lock

   Windows（cmd）：

   .. code-block:: bat

      del \path\to\project\.esp_bmgr_py.lock

   Windows（PowerShell）：

   .. code-block:: powershell

      Remove-Item \path\to\project\.esp_bmgr_py.lock

3. 工程目录不可写时锁文件会回退到系统临时目录的 ``esp_bmgr_py_locks/<digest>.lock``\ （Linux/macOS 通常是 ``/tmp/``，Windows 通常是 ``%TEMP%``），提示信息中会显示具体路径。
4. 需要更长的等待窗口（例如首次拉取组件较慢时）可调整超时：

   Linux / macOS：

   .. code-block:: bash

      export ESP_BMGR_LOCK_TIMEOUT=120

   Windows（cmd）：

   .. code-block:: bat

      set ESP_BMGR_LOCK_TIMEOUT=120

   Windows（PowerShell）：

   .. code-block:: powershell

      $env:ESP_BMGR_LOCK_TIMEOUT = "120"

完整说明见 ``esp_board_manager/docs/esp_bmgr_assist_cn.md``。

切换 IDF 版本后选项不识别
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

切换 IDF 版本后，``idf.py bmgr`` 可能出现选项不识别的报错，例如：

.. code-block:: text

   >> idf.py bmgr -l
   Usage: idf.py bmgr [OPTIONS]
   Try 'idf.py bmgr --help' for help.

   Error: No such option: -l

原因是 ESP-IDF 各版本使用独立的 Python 虚拟环境，切换版本后新环境中可能未安装 ``esp-bmgr-assist``。

处理方式：

1. 检查当前 IDF Python 环境中是否存在该包：

   .. code-block:: bash

      pip show esp-bmgr-assist

2. 若未显示包信息，在当前 IDF 环境中重新安装或升级：

   .. code-block:: bash

      python3 -m pip install --upgrade esp-bmgr-assist
