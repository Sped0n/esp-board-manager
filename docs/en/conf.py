# type: ignore
# -*- coding: utf-8 -*-

try:
    from conf_common import *  # noqa: F403,F401
except ImportError:
    import os
    import sys

    sys.path.insert(0, os.path.abspath('..'))
    from conf_common import *  # noqa: F403,F401

import datetime

current_year = datetime.datetime.now().year

project = u'Espressif Board Manager Guide'
copyright = u'2017 - {}, Espressif Systems (Shanghai) Co., Ltd'.format(current_year)
pdf_title = u'Espressif Board Manager Guide'
language = 'en'
html_title = 'Espressif Board Manager Guide'
