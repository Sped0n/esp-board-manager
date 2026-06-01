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

project = u'乐鑫板卡管理指南'
copyright = u'2017 - {}, 乐鑫信息科技（上海）股份有限公司'.format(current_year)
pdf_title = u'乐鑫板卡管理指南'
language = 'zh_CN'
html_title = '乐鑫板卡管理指南'

