Migrating from Manual Board Initialization to BMGR
=====================================================

:link_to_translation:`zh_CN:[中文]`

This page is intended for existing projects and describes the migration steps, recommended pace, and which code is appropriate to retain as board-level customization.

Migration steps:

- Inventory the existing board initialization: identify what peripheral initializations, device initializations, and board-specific logic are present.
- Extract peripherals: start by consolidating low-level resources such as I2C, SPI, I2S, GPIO, ADC, and SDMMC into YAML.
- Extract devices: gradually migrate device types that BMGR can already express — ``audio_codec``, ``display_lcd``, ``button``, ``camera``, etc. — into YAML.
- Converge to a unified API: prefer accessing resources through interfaces such as ``esp_board_manager_get_*()``, ``esp_board_manager_init_*()``, and similar at the application layer.
- Adopt a reversible migration pace: migrate one peripheral or one device at a time, paired with minimal regression testing.
- Clarify which code does not need to be YAML-ized: code that has a strong dependency on vendor-private initialization flows, complex timing, or closed-source driver entry points can remain in ``setup_device.c``.
- AI assistance for migration is acceptable, but must not skip manual review.
- Prepare a regression checklist to verify after migration is complete.
