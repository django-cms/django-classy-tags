# -*- coding: utf8 -*-
# flake8: NOQA
import sys


PY2 = sys.version_info[0] == 2

if PY2:
    string_types = (basestring,)
else:
    string_types = (str,)
