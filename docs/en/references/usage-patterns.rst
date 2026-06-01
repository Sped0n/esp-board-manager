Examples
========

:link_to_translation:`zh_CN:[中文]`

``esp_board_manager/examples/`` provides standalone buildable examples that demonstrate the complete workflow: selecting a board, generating board-level code, initializing the board, and obtaining device handles by name. Each example directory includes a ``README.md`` with hardware requirements and build instructions.

.. list-table::
   :header-rows: 1
   :widths: 22 38 40

   * - Example
     - Typical Use Case
     - Primary Devices Involved
   * - ``play_embed_music``
     - Play a WAV prompt tone embedded in firmware
     - ``audio_codec`` (DAC)
   * - ``play_sdcard_music``
     - Play a WAV file from a microSD card
     - ``audio_codec``, ``fs_fat``
   * - ``record_to_sdcard``
     - Record microphone input and write to SD card as WAV
     - ``audio_codec`` (ADC), ``fs_fat``
   * - ``record_and_play``
     - Capture microphone input and play it back in real time (loopback)
     - ``audio_codec`` (ADC + DAC)
   * - ``display_lvgl``
     - Initialize LCD and touchscreen, run the LVGL test UI
     - ``display_lcd``, ``lcd_touch``

``examples/common/`` provides shared utilities such as WAV header parsing, used by the SD card-related examples.

Before running an example, ensure the target board has the required devices configured in ``board_devices.yaml`` (for example, ``audio_adc`` and ``audio_dac`` for Korvo-class boards, ``fs_fat`` for boards with an SD card slot, and ``display_lcd`` for boards with a display). After switching boards, re-run ``idf.py bmgr -b <board>`` before building.

Test Apps
---------

``esp_board_manager/test_apps/`` provides test applications designed for CI and local validation. They cover the board initialization flow across a variety of board configurations. After completing a new board integration, run the test app to fully verify the correctness of the generated code.
