parser 的组织方式
========================

:link_to_translation:`en:[English]`

本节说明 ``devices/dev_xxx/dev_xxx.py`` 与 ``peripherals/periph_xxx/periph_xxx.py`` 的职责，以及模板 YAML 与生成逻辑的关系。

规划要点：

- parser 如何读取 YAML。
- parser 如何输出 C 配置结构体。
- parser 如何处理版本、默认值、枚举与字段校验。
- parser 与模板文档如何保持一致。

