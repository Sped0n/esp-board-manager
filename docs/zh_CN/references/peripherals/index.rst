外设参考
============

:link_to_translation:`en:[English]`

外设参考按 peripheral type 单独介绍其用途、YAML 配置和常见约束。这一节只讲 peripheral 自身的配置和约束，不重复 device 级组合逻辑，也不重复通用板级工作流。

公共字段语法（``name`` / ``type`` / ``role`` / ``format``、``[IO]`` / ``[TO_BE_CONFIRMED]`` 等）见 :doc:`/programming-guide/board-directory` 与 :doc:`/programming-guide/yaml-rules`。

.. toctree::
   :maxdepth: 1
   :caption: 外设列表

   i2c
   spi
   i2s
   uart
   gpio
   adc
   dac
   ledc
   pcnt
   rmt
   mcpwm
   sdm
   anacmpr
   dsi
   ldo
