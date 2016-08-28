from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string

from classytags.core import Tag
from classytags.utils import flatten_context


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
        if varname:
            value = self.get_value_for_context(context, **kwargs)
            context[varname] = value
            return ''
        else:
            value = self.get_value(context, **kwargs)
        return value

    def get_value_for_context(self, context, **kwargs):
        """
        Called when a value for a varname (in the "as varname" case) should is
        requested. This can be used to for example suppress exceptions in this
        case.

        Returns the value to be set.
        """
        return self.get_value(context, **kwargs)

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
    push_context = False

    def render_tag(self, context, **kwargs):
        """
        INTERNAL!

        Gets the context and data to render.
        """
        template = self.get_template(context, **kwargs)
        if self.push_context:
            safe_context = flatten_context(context)
            data = self.get_context(safe_context, **kwargs)
            safe_context.update(**data)
            output = render_to_string(template, safe_context)
        else:
            new_context = context.new(
                flatten_context(self.get_context(context, **kwargs))
            )
            data = flatten_context(new_context)
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
