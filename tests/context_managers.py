from django import template
from django.conf import settings
from django.template.engine import Engine


builtins = Engine.get_default().template_builtins


class NULL:
    pass


class SettingsOverride:  # pragma: no cover
    """
    Overrides Django settings within a context and resets them to their inital
    values on exit.

    Example:

        with SettingsOverride(DEBUG=True):
            # do something
    """
    def __init__(self, **overrides):
        self.overrides = overrides

    def __enter__(self):
        self.old = {}
        for key, value in self.overrides.items():
            self.old[key] = getattr(settings, key, NULL)
            setattr(settings, key, value)

    def __exit__(self, type, value, traceback):
        for key, value in self.old.items():
            if value is not NULL:
                setattr(settings, key, value)
            else:
                delattr(settings, key)  # do not pollute the context!


class TemplateTags:  # pragma: no cover
    def __init__(self, *tags):
        self.lib = template.Library()
        for tag in tags:
            self.lib.tag(tag)

    def __enter__(self):
        self.old = list(builtins)
        builtins.insert(0, self.lib)

    def __exit__(self, type, value, traceback):
        builtins[:] = self.old
