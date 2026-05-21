Peripheral Reference
====================

:link_to_translation:`zh_CN:[中文]`

The peripheral reference covers each peripheral type individually, describing its purpose, YAML configuration, and common constraints. This section only discusses the configuration and constraints of the peripheral itself; it does not repeat device-level combination logic or the general board-level workflow.

For common field syntax (``name`` / ``type`` / ``role`` / ``format``, ``[IO]`` / ``[TO_BE_CONFIRMED]``, etc.), see :doc:`/programming-guide/board-directory` and :doc:`/programming-guide/yaml-rules`.

.. toctree::
   :maxdepth: 1
   :caption: Peripheral List

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
