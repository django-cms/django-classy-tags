from classytags.utils import TemplateConstant, NULL, ResolvableList
from classytags.exceptions import InvalidFlag
from django.core.exceptions import ImproperlyConfigured

class Argument(object):
    """
    A basic single value argument.
    """
    def __init__(self, name, default=None, required=True):
        self.name = name
        self.default = default
        self.required = required
        
    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.name)
        
    def get_default(self):
        """
        Get the default value
        """
        return TemplateConstant(self.default)
        
    def parse(self, parser, token, tagname, kwargs):
        """
        Parse a token.
        """
        if self.name in kwargs:
            return False
        else:
            kwargs[self.name] = parser.compile_filter(token)
            return True
    
    
class MultiValueArgument(Argument):
    """
    An argument which allows multiple values.
    """
    def __init__(self, name, default=NULL, required=True, max_values=None):
        self.max_values = max_values
        if default is NULL:
            default = []
        super(MultiValueArgument, self).__init__(name, default, required)
        
    def parse(self, parser, token, tagname, kwargs):
        """
        Parse a token.
        """
        if self.name in kwargs:
            if self.max_values and len(kwargs[self.name]) == self.max_values:
                return False
            kwargs[self.name].append(parser.compile_filter(token))
        else:
            kwargs[self.name] = ResolvableList(parser.compile_filter(token))
        return True


class Flag(Argument):
    """
    A boolean flag
    """
    def __init__(self, name, default=NULL, true_values=None, false_values=None,
                 case_sensitive=False):
        if default is not NULL:
            required = False
        else:
            required = True
        super(Flag, self).__init__(name, default, required)
        if true_values is None:
            true_values = []
        if false_values is None:
            false_values = []
        if isinstance(true_values, basestring):
            true_values = [true_values]
        if isinstance(false_values, basestring):
            false_values = [false_values]
        if not case_sensitive:
            self.mod = lambda x: x.lower()
        else:
            self.mod = lambda x: x
        self.true_values = [self.mod(tv) for tv in true_values]
        self.false_values = [self.mod(fv) for fv in false_values]
        if not any([self.true_values, self.false_values]):
            raise ImproperlyConfigured(
                "Flag must specify either true_values and/or false_values"
            )
        
    def parse(self, parser, token, tagname, kwargs):
        """
        Parse a token.
        """
        ltoken = self.mod(token)
        if self.name in kwargs:
            return False
        if self.true_values and ltoken in self.true_values:
            kwargs[self.name] = TemplateConstant(True)
        elif self.false_values and ltoken in self.false_values:
            kwargs[self.name] = TemplateConstant(False)
        elif self.default is NULL:
            allowed_values = []
            if self.true_values:
                allowed_values += self.true_values
            if self.false_values:
                allowed_values += self.false_values
            raise InvalidFlag(self.name, token, allowed_values, tagname)
        else:
            kwargs[self.name] = self.default
        return True