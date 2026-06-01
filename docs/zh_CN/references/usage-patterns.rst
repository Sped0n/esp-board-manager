示例
==========================================================================

:link_to_translation:`en:[English]`

``esp_board_manager/examples/`` 提供若干可独立构建的示例，演示完整的使用路径：选择开发板、生成板级代码、初始化、按设备名获取句柄。各例程目录下提供 ``README_CN.md``，其中包含硬件要求与构建步骤。

.. list-table::
   :header-rows: 1
   :widths: 22 38 40

   * - 例程
     - 典型场景
     - 主要涉及的 device
   * - ``play_embed_music``
     - 从固件内嵌 WAV 播放提示音
     - ``audio_codec``\ （DAC）
   * - ``play_sdcard_music``
     - 从 microSD 卡播放 WAV
     - ``audio_codec``、``fs_fat``
   * - ``record_to_sdcard``
     - 麦克风录音并写入 SD 卡 WAV
     - ``audio_codec``\ （ADC）、``fs_fat``
   * - ``record_and_play``
     - 麦克风采集并实时从扬声器播放（回环）
     - ``audio_codec``\ （ADC + DAC）
   * - ``display_lvgl``
     - 初始化 LCD 与触摸屏，运行 LVGL 测试 UI
     - ``display_lcd``、``lcd_touch``

``examples/common/`` 提供 WAV 头解析等共用代码，供 SD 卡相关例程引用。

使用前，对应开发板需已在 ``board_devices.yaml`` 中配置相应设备（例如 Korvo 类开发板的 ``audio_adc`` 与 ``audio_dac``，带 SD 槽开发板的 ``fs_fat``，带显示屏开发板的 ``display_lcd``）。切换开发板后需重新执行 ``idf.py bmgr -b <board>`` 再进行构建。

测试应用
--------

``esp_board_manager/test_apps/`` 提供面向 CI 和本地验证的测试应用，覆盖板级初始化流程与多种开发板配置。在完成新开发板适配后，可用该测试应用全面验证生成代码的正确性。
