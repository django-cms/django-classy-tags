from operator import attrgetter

from django.template import Node

from classytags.blocks import BlockDefinition
from classytags.parser import Parser
from classytags.utils import StructuredOptions, get_default_name


class Options:
    """
    Option class holding the arguments of a tag.
    """
    def __init__(self, *options, **kwargs):
        self._options = options
        self._kwargs = kwargs
        self.options = {}
        self.raw_options = options
        self.breakpoints = []
        self.combined_breakpoints = {}
        current_breakpoint = None
        last = None
        self.options[current_breakpoint] = []
        self.all_argument_names = []
        for value in options:
            if isinstance(value, str):
                if isinstance(last, str):
                    self.combined_breakpoints[last] = value
                self.breakpoints.append(value)
                current_breakpoint = value
                self.options[current_breakpoint] = []
            else:
                self.options[current_breakpoint].append(value)
                self.all_argument_names.append(value.name)
            last = value
        self.blocks = []
        for block in kwargs.get('blocks', []):
            if isinstance(block, BlockDefinition):
                block_definition = block
            elif isinstance(block, str):
                block_definition = BlockDefinition(block, block)
            else:
                block_definition = BlockDefinition(block[1], block[0])
            block_definition.validate(self)
            self.blocks.append(block_definition)
        if 'parser_class' in kwargs:
            self.parser_class = kwargs['parser_class']
        else:
            self.parser_class = Parser

    def __repr__(self):
        bits = list(map(repr, self.options[None]))
        for breakpoint in self.breakpoints:
            bits.append(breakpoint)
            for option in self.options[breakpoint]:
                bits.append(repr(option))
        options = ','.join(bits)
        if self.blocks:
            blocks = ';%s' % ','.join(map(attrgetter('alias'), self.blocks))
        else:  # pragma: no cover
            blocks = ''
        return f'<Options:{options}{blocks}>'

    def __add__(self, other):
        if not isinstance(other, Options):
            raise TypeError("Cannot add Options to non-Options object")
        if self.blocks and other.blocks:
            raise ValueError(
                "Cannot add two Options objects if both objects define blocks"
            )
        if self.parser_class is not other.parser_class:
            raise ValueError(
                "Cannot add two Options objects with different parser classes"
            )
        full_options = self._options + other._options
        full_kwargs = {
            'parser_class': self.parser_class
        }
        if self._kwargs.get('blocks', False):
            full_kwargs['blocks'] = self._kwargs['blocks']
        elif other._kwargs.get('blocks', False):
            full_kwargs['blocks'] = other._kwargs['blocks']
        return Options(*full_options, **full_kwargs)

    def get_parser_class(self):
        return self.parser_class

    def bootstrap(self):
        """
        Bootstrap this options
        """
        return StructuredOptions(
            self.options,
            self.breakpoints,
            self.blocks,
            self.combined_breakpoints
        )

    def parse(self, parser, tokens):
        """
        Parse template tokens into a dictionary
        """
        argument_parser_class = self.get_parser_class()
        argument_parser = argument_parser_class(self)
        return argument_parser.parse(parser, tokens)


class TagMeta(type):
    """
    Metaclass for the Tag class that set's the name attribute onto the class
    and a _decorated_function pseudo-function which is used by Django's
    template system to get the tag name.
    """
    def __new__(cls, name, bases, attrs):
        parents = [base for base in bases if isinstance(base, TagMeta)]
        if not parents:
            return super().__new__(cls, name, bases, attrs)
        tag_name = str(attrs.get('name', get_default_name(name)))

        def fake_func():
            pass  # pragma: no cover

        fake_func.__name__ = tag_name
        attrs['_decorated_function'] = fake_func
        attrs['name'] = str(tag_name)
        return super().__new__(cls, name, bases, attrs)


class Tag(TagMeta('TagMeta', (Node,), {})):
    """
    Main Tag class.
    """
    options = Options()
    name = None

    def __init__(self, parser, tokens):
        self.kwargs, self.blocks = self.options.parse(parser, tokens)
        self.child_nodelists = []
        for key, value in self.blocks.items():
            setattr(self, key, value)
            self.child_nodelists.append(key)

    def render(self, context):
        """
        INTERNAL method to prepare rendering
        Usually you should not override this method, but rather use render_tag.
        """
        items = self.kwargs.items()
        kwargs = {key: value.resolve(context) for key, value in items}
        kwargs.update(self.blocks)
        return str(self.render_tag(context, **kwargs))

    def render_tag(self, context, **kwargs):
        """
        The method you should override in your custom tags
        """
        raise NotImplementedError

    def __repr__(self):
        return '<Tag: %s>' % self.name
