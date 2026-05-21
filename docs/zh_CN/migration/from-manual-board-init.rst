从手写板级初始化迁移到 BMGR
================================

:link_to_translation:`en:[English]`

本页面向已有项目，说明迁移步骤、推荐节奏，以及哪些代码适合保留为板级自定义。

迁移步骤：

- 梳理现有板级初始化清单：peripheral 初始化、device 初始化与纯板级差异逻辑分别有哪些。
- 抽取 peripheral：优先将 I2C、SPI、I2S、GPIO、ADC、SDMMC 等底层资源收敛到 YAML。
- 抽取 device：将已能由 BMGR 表达的 ``audio_codec``、``display_lcd``、``button``、``camera`` 等逐步迁入 YAML。
- 收敛到统一 API：应用层优先通过 ``esp_board_manager_get_*()``、``esp_board_manager_init_*()`` 等接口访问资源。
- 采用可回退的迁移节奏：一次只迁一个 peripheral 或一个 device，并配合最小回归测试。
- 明确哪些代码不必强行 YAML 化：强依赖板厂私有初始化流程、复杂时序或闭源驱动入口的部分可保留在 ``setup_device.c`` 中。
- 可借助 AI 辅助迁移，但不应跳过人工复核。
- 准备迁移完成后的回归检查清单。

