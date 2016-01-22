# -*- coding: utf-8 -*-
# flake8: noqa

try:  # pragma: no cover
    compat_basestring = basestring
except NameError:
    compat_basestring = str

try:
    compat_next = next
except NameError:  # pragma: no cover
    def compat_next(it):
        return it.next()
