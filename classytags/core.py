from classytags.parser import Parser
from classytags.utils import StructuredOptions
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
        self.parser = Parser(self)

    def bootstrap(self):
        """
        Bootstrap this options
        """
        return StructuredOptions(self.options, self.breakpoints)
        
    def parse(self, parser, tokens):
        """
        Parse template tokens into a dictionary
        """
        return self.parser.parse(parser, tokens)


class Tag(Node):
    """
    Tag class.
    """
    __name__ = ''
    options = Options()
    
    def __init__(self, parser, tokens):
        self.kwargs = self.options.parse(parser, tokens)
            
    def render(self, context):
        """
        INTERNAL method to prepare rendering
        """
        kwargs = dict([(k, v.resolve(context)) for k,v in self.kwargs.items()])
        return self.render_tag(context, **kwargs)
        
    def render_tag(self, context, **kwargs):
        """
        The method you should override in your custom tags
        """
        return ''
        
    def __repr__(self):
        '<Tag: %s>' % self.__name__