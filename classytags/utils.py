from copy import copy
from classytags.compat import compat_basestring
import re


class NULL:
    """
    Internal type to differentiate between None and No-Input
    """


class TemplateConstant(object):
    """
    A 'constant' internal template variable which basically allows 'resolving'
    returning it's initial value
    """
    def __init__(self, value):
        self.literal = value
        if isinstance(value, compat_basestring):
            self.value = value.strip('"\'')
        else:
            self.value = value

    def __repr__(self):  # pragma: no cover
        return '<TemplateConstant: %s>' % repr(self.value)

    def resolve(self, context):
        return self.value


class StructuredOptions(object):
    """
    Bootstrapped options
    """
    def __init__(self, options, breakpoints, blocks, combind_breakpoints):
        self.options = options
        self.breakpoints = copy(breakpoints)
        self.blocks = copy(blocks)
        self.combined_breakpoints = dict(combind_breakpoints.items())
        self.reversed_combined_breakpoints = dict((v,k) for k,v in combind_breakpoints.items())
        self.current_breakpoint = None
        if self.breakpoints:
            self.next_breakpoint = self.breakpoints.pop(0)
        else:
            self.next_breakpoint = None

    def shift_breakpoint(self):
        """
        Shift to the next breakpoint
        """
        self.current_breakpoint = self.next_breakpoint
        if self.breakpoints:
            self.next_breakpoint = self.breakpoints.pop(0)
        else:
            self.next_breakpoint = None

    def get_arguments(self):
        """
        Get the current arguments
        """
        return copy(self.options[self.current_breakpoint])


_re1 = re.compile('(.)([A-Z][a-z]+)')
_re2 = re.compile('([a-z0-9])([A-Z])')


def get_default_name(name):
    """
    Turns "CamelCase" into "camel_case"
    """
    return _re2.sub(r'\1_\2', _re1.sub(r'\1_\2', name)).lower()


def mixin(parent, child, attrs={}):
    return type(
        '%sx%s' % (parent.__name__, child.__name__),
        (child, parent),
        attrs
    )
