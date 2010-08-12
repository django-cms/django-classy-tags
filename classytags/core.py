from classytags.parser import Parser
from classytags.utils import StructuredOptions, get_default_name
from django.template import Node


class Options(object):
    """
    Option class holding the arguments of a tag.
    """
    def __init__(self, *options):
        self.options = {}
        self.breakpoints = []
        current_breakpoint = None
        self.options[current_breakpoint] = []
        for value in options:
            if isinstance(value, basestring):
                self.breakpoints.append(value)
                current_breakpoint = value
                self.options[current_breakpoint] = []
            else:
                self.options[current_breakpoint].append(value)
        self.argument_parser_class = self.get_parser_class()
    
    def get_parser_class(self):
        return Parser

    def bootstrap(self):
        """
        Bootstrap this options
        """
        return StructuredOptions(self.options, self.breakpoints)
        
    def parse(self, parser, tokens):
        """
        Parse template tokens into a dictionary
        """
        argument_parser = self.argument_parser_class(self)
        return argument_parser.parse(parser, tokens)


class TagMeta(type):
    def __new__(cls, name, bases, attrs):
        parents = [base for base in bases if isinstance(base, TagMeta)]
        if not parents:
            return super(TagMeta, cls).__new__(cls, name, bases, attrs)
        tag_name = attrs.get('name', get_default_name(name))
        def fake_func(): pass
        fake_func.__name__ = tag_name
        attrs['_decorated_function'] = fake_func
        return super(TagMeta, cls).__new__(cls, name, bases, attrs)


class Tag(Node):
    """
    Tag class.
    """
    __metaclass__ = TagMeta
    
    options = Options()
    
    def __init__(self, parser, tokens):
        self.kwargs = self.options.parse(parser, tokens)
            
    def render(self, context):
        """
        INTERNAL method to prepare rendering
        """
        kwargs = dict([(k, v.resolve(context)) for k,v in self.kwargs.items()])
        return self.render_tag(context, **kwargs)
        
    def render_tag(self, context, **kwargs): # pragma: no cover
        """
        The method you should override in your custom tags
        """
        return ''
        
    def __repr__(self):
        '<Tag: %s>' % self.__name__