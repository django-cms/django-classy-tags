# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured


def _collect(name, parser):
    collector = getattr(name, 'collect', None)
    if callable(collector):
        return collector(parser)
    return name


class BlockDefinition(object):
    """
    Definition of 'parse-until-blocks' used by the parser.
    """
    def __init__(self, alias, *names):
        self.alias = alias
        self.names = names

    def validate(self, options):
        for name in self.names:
            validator = getattr(name, 'validate', None)
            if callable(validator):
                validator(options)

    def collect(self, parser):
        return [_collect(name, parser) for name in self.names]


class VariableBlockName(object):
    def __init__(self, template, argname):
        self.template = template
        self.argname = argname

    def validate(self, options):
        if self.argname not in options.all_argument_names:
            raise ImproperlyConfigured(
                "Invalid block definition, %r not a valid argument name, "
                "available argument names: %r" % (self.argname,
                                                  options.all_argument_names)
            )

    def collect(self, parser):
        value = parser.kwargs[self.argname]
        return self.template % {'value': value.literal}
