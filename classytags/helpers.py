from classytags.core import Tag
from django.core.exceptions import ImproperlyConfigured
from django.template.context import Context
from django.template.loader import render_to_string


class AsTag(Tag):
    """
    Same as tag but allows for an optional 'as varname'. The 'as varname'
    options must be added 'manually' to the options class.
    """
    def __init__(self, parser, tokens):
        super(AsTag, self).__init__(parser, tokens)
        if len(self.options.breakpoints) < 1:
            raise ImproperlyConfigured(
                "AsTag subclasses require at least one breakpoint."
            )
        last_breakpoint = self.options.options[self.options.breakpoints[-1]]
        optscount = len(last_breakpoint)
        if optscount != 1:
            raise ImproperlyConfigured(
                "The last breakpoint of AsTag subclasses require exactly one "
                "argument, got %s instead." % optscount
            )
        self.varname_name = last_breakpoint[-1].name

    def render_tag(self, context, **kwargs):
        """
        INTERNAL!

        Get's the value for the current context and arguments and puts it into
        the context if needed or returns it.
        """
        varname = kwargs.pop(self.varname_name)
        value = self.get_value(context, **kwargs)
        if varname:
            context[varname] = value
            return ''
        return value

    def get_value(self, context, **kwargs):
        """
        Returns the value for the current context and arguments.
        """
        raise NotImplementedError


class InclusionTag(Tag):
    """
    A helper Tag class which allows easy inclusion tags.

    The template attribute must be set.

    Instead of render_tag, override get_context in your subclasses.

    Optionally override get_template in your subclasses.
    """
    template = None

    def __init__(self, parser, tokens):
        super(InclusionTag, self).__init__(parser, tokens)
        if self.template is None:
            raise ImproperlyConfigured(
                "InclusionTag subclasses require the template attribute to be "
                "set."
            )

    def render_tag(self, context, **kwargs):
        """
        INTERNAL!

        Gets the context and data to render.
        """
        template = self.get_template(context, **kwargs)
        data = self.get_context(context, **kwargs)
        output = render_to_string(template, data)
        return output

    def get_template(self, context, **kwargs):
        """
        Returns the template to be used for the current context and arguments.
        """
        return self.template

    def get_context(self, context, **kwargs):
        """
        Returns the context to render the template with.
        """
        return {}
