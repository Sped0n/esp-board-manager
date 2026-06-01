版本迁移
============

:link_to_translation:`en:[English]`

本页说明升级 BMGR 或 ESP-IDF 后的迁移步骤与重点检查项，便于用户在 changelog 之外快速定位需要关注的内容。

规划要点：

- 版本迁移需区分三类变化：ESP-IDF 版本变化、BMGR 运行时 API 或生成逻辑变化、YAML schema 或字段语义变化。
- 建议固定一个可工作的旧版本基线。
- 推荐流程：先阅读 migration notes 与 breaking changes，再重新执行 ``idf.py bmgr -b <board>``，然后比较 ``gen_bmgr_codes``、``board_manager.defaults``、``Kconfig.projbuild``，最后进行完整构建与最小运行时回归。
- 升级 BMGR 时重点关注命令入口、生成文件、宏命名、组件依赖与默认配置注入方式是否变化。
- 升级 ESP-IDF 时重点关注底层驱动 API、默认配置项、Kconfig 选项、组件依赖与头文件路径是否变化。
- 当 YAML schema 升级时，建议提供旧写法到新写法的对照表。
- 不建议将旧版本生成物直接拷贝到新版本继续使用。
- 准备版本迁移检查清单。

