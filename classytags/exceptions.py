from django.template import TemplateSyntaxError

__all__ =  ['ArgumentRequiredError', 'InvalidFlag', 'BreakpointExpected',
            'TooManyArguments']


class BaseError(TemplateSyntaxError):
    template = ''
    
    def __str__(self): # pragma: no cover
        return self.template % self.__dict__


class ArgumentRequiredError(BaseError):
    template = "The tag '%(tagname)s' requires the '%(argname)s' argument."
    
    def __init__(self, argument, tagname):
        self.argument = argument
        self.tagname = tagname 
        self.argname = self.argument.name
        
        
class InvalidFlag(BaseError):
    template = ("The flag '%(argname)s' for the tag '%(tagname)s' must be one "
                "of %(allowed_values)s, but got '%(actual_value)s'")
    
    def __init__(self, argname, actual_value, allowed_values, tagname):
        self.argname = argname
        self.tagname = tagname
        self.actual_value = actual_value
        self.allowed_values = allowed_values


class BreakpointExpected(BaseError):
    template = ("Expected one of the following breakpoints: %(breakpoints)s in "
                "%(tagname)s, got '%(got)s' instead.")
    
    def __init__(self, tagname, breakpoints, got):
        self.breakpoints = ', '.join(["'%s'" % bp for bp in breakpoints])
        self.tagname = tagname
        self.got = got


class TooManyArguments(BaseError):
    template = "The tag '%(tagname)s' got too many arguments: %(extra)s"
    
    def __init__(self, tagname, extra):
        self.tagname = tagname
        self.extra = ', '.join(["'%s'" % e for e in extra])
        
        
class TemplateSyntaxWarning(Warning):
    """
    Used for variable cleaning TemplateSyntaxErrors when in non-debug-mode.
    """