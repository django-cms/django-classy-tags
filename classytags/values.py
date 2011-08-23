from classytags.exceptions import TemplateSyntaxWarning
from django import template
from django.conf import settings
import warnings


class StringValue(object):
    errors = {}
    value_on_error = ""

    def __init__(self, var):
        self.var = var
        if hasattr(self.var, 'literal'):  # django.template.base.Variable
            self.literal = self.var.literal
        else:  # django.template.base.FilterExpression
            self.literal = self.var.token

    def resolve(self, context):
        resolved = self.var.resolve(context)
        return self.clean(resolved)

    def clean(self, value):
        return value

    def error(self, value, category):
        data = self.get_extra_error_data()
        data['value'] = repr(value)
        message = self.errors.get(category, "") % data
        if settings.DEBUG:
            raise template.TemplateSyntaxError(message)
        else:
            warnings.warn(message, TemplateSyntaxWarning)
            return self.value_on_error

    def get_extra_error_data(self):
        return {}


class StrictStringValue(StringValue):
    errors = {
        "clean": "%(value)s is not a string",
    }
    value_on_error = ""

    def clean(self, value):
        if not isinstance(value, basestring):
            return self.error(value, "clean")
        return value


class IntegerValue(StringValue):
    errors = {
        "clean": "%(value)s could not be converted to Integer",
    }
    value_on_error = 0

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


class DictValue(dict, StringValue):
    def __init__(self, value):
        dict.__init__(self, value)

    def resolve(self, context):
        resolved = dict(
            [(key, value.resolve(context)) for key, value in self.items()]
        )
        return self.clean(resolved)


class ChoiceValue(object):
    errors = {
        "choice": "%(value)s is not a valid choice. Valid choices: "
                  "%(choices)s.",
    }
    choices = []

    def clean(self, value):
        cleaned = super(ChoiceValue, self).clean(value)
        if cleaned in self.choices:
            return cleaned
        else:
            return self.error(cleaned, "choice")

    def get_extra_error_data(self):
        data = super(ChoiceValue, self).get_extra_error_data()
        data['choices'] = self.choices
        return data
