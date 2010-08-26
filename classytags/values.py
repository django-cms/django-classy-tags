from classytags.exceptions import TemplateSyntaxWarning
from django import template
from django.conf import settings
import warnings


class StringValue(object):
    errors = {}
    value_on_error = ""
    
    def __init__(self, var):
        self.var = var
        
    def resolve(self, context):
        resolved = self.var.resolve(context)
        return self.clean(resolved)
    
    def clean(self, value):
        return value
    
    def error(self, value, category):
        message = self.errors.get(category, "") % {'value': repr(value)}
        if settings.DEBUG:
            raise template.TemplateSyntaxError(message)
        else:
            warnings.warn(message, TemplateSyntaxWarning)
            return self.value_on_error


class IntegerValue(StringValue):
    errors = {
        "clean": "%(value)s could not be converted to Integer",
    }
    
    def clean(self, value):
        try:
            return int(value)
        except ValueError:
            return self.error(value, "clean")


class ListValue(list, StringValue):
    """
    A list of template variables for easy resolving
    """
    def __init__(self, value):
        list.__init__(self)
        self.append(value)
        
    def resolve(self, context):
        resolved = [item.resolve(context) for item in self]
        return self.clean(resolved)