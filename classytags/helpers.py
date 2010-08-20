from classytags.core import Tag

class AsTag(Tag):
    """
    Same as tag but allows for an optional 'as varname'. The 'as varname'
    options must be added 'manually' to the options class.
    """
    @property
    def varname_name(self):
        return self.options.options[self.options.breakpoints[-1]][-1].name
    
    def render_tag(self, context, **kwargs):
        varname = kwargs.pop(self.varname_name)
        value = self.get_value(context, **kwargs)
        if varname:
            context[varname] = value
            return ''
        return value
    
    def get_value(self, context, **kwargs): # pragma: no cover
        raise NotImplementedError