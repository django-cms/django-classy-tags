from django.template import TemplateSyntaxError

__all__ =  ['ArgumentRequiredError']


class BaseError(TemplateSyntaxError):
    template = ''
    
    def __str__(self):
        return self.template % self.__dict__


class ArgumentRequiredError(BaseError):
    template = "The tag '%(tagname)s' requires the '%(argname)s' argument."
    
    def __init__(self, argument, tagname):
        self.argument = argument
        self.tagname = tagname 
        self.argument = self.argname.name
        
        
class InvalidFlag(BaseError):
    template = ("The flag '%(argname)s' for the tag '%(tagname)s' must be one "
                "of %(allowed_values)s, but got '%(actual_value)s'")
    
    def __init__(self, argname, actual_value, allowed_values, tagname):
        self.argname = argname
        self.tagname = tagname
        self.actual_value = actual_value
        self.allowed_values = allowed_values
        