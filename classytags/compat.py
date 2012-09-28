# -*- coding: utf-8 -*-

try:
    compat_basestring = basestring
except NameError:
    compat_basestring = str

try:
    compat_next = next
except NameError:
    def compat_next(it):
        return it.next()
