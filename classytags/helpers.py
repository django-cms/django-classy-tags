from classytags.core import Tag
from django.template.loader import render_to_string
from django.core.exceptions import ImproperlyConfigured

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
        varname = kwargs.pop(self.varname_name)
        value = self.get_value(context, **kwargs)
        if varname:
            context[varname] = value
            return ''
        return value
    
    def get_value(self, context, **kwargs):
        raise NotImplementedError
    
    
class InclusionTag(Tag):
    template = None
    
    def __init__(self, parser, tokens):
        super(InclusionTag, self).__init__(parser, tokens)
        if self.template is None:
            raise ImproperlyConfigured(
                "InclusionTag subclasses require the template attribute to be "
                "set."
            )
    
    def render_tag(self, context, **kwargs):
        template = self.get_template(context, **kwargs)
        data = self.get_context(context, **kwargs)
        return render_to_string(template, data)
    
    def get_template(self, context, **kwargs):
        return self.template
    
    def get_context(self, context, **kwargs):
        return {}