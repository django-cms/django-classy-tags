from classytags.exceptions import (BreakpointExpected, TooManyArguments,
    ArgumentRequiredError)
from copy import deepcopy
from django import template


class Parser(object):
    """
    Argument parsing class. A new instance of this gets created each time a tag
    get's parsed.
    """
    def __init__(self, options):
        self.options = options.bootstrap()

    def parse(self, parser, tokens):
        """
        Parse a token stream
        """
        self.parser = parser
        self.bits = tokens.split_contents()
        self.tagname = self.bits.pop(0)
        self.kwargs = {}
        self.blocks = {}
        # Get the first chunk of arguments until the next breakpoint
        self.arguments = self.options.get_arguments()
        self.current_argument = None
        # get a copy of the bits (tokens)
        self.todo = list(self.bits)
        # parse the bits (tokens)
        for bit in self.bits:
            self.handle_bit(bit)
        # finish the bits (tokens)
        self.finish()
        # parse block tags
        self.parse_blocks()
        return self.kwargs, self.blocks

    def handle_bit(self, bit):
        """
        Handle the current bit
        """
        # Check if the current bit is the next breakpoint
        if bit == self.options.next_breakpoint:
            self.handle_next_breakpoint(bit)
        # Check if the current bit is a future breakpoint
        elif bit in self.options.breakpoints:
            self.handle_breakpoints(bit)
        # Otherwise it's a 'normal' argument
        else:
            self.handle_argument(bit)
        # remove from todos
        del self.todo[0]

    def handle_next_breakpoint(self, bit):
        """
        Handle a bit which is the next breakpoint by checking the current
        breakpoint scope is finished or can be finished and then shift to the
        next scope.
        """
        # Check if any unhandled argument in the current breakpoint is required
        self.check_required()
        # Shift the breakpoint to the next one
        self.options.shift_breakpoint()
        # Get the next chunk of arguments
        self.arguments = self.options.get_arguments()
        self.current_argument = self.arguments.pop(0)

    def handle_breakpoints(self, bit):
        """
        Handle a bit which is a future breakpoint by trying to finish all
        intermediate breakpoint codes as well as the current scope and then
        shift.
        """
        # While we're not at our target breakpoint
        while bit != self.options.current_breakpoint:
            # Check required arguments
            self.check_required()
            # Shift to the next breakpoint
            self.options.shift_breakpoint()
            self.arguments = self.options.get_arguments()
        self.current_argument = self.arguments.pop(0)

    def handle_argument(self, bit):
        """
        Handle the current argument.
        """
        # If we don't have an argument yet
        if self.current_argument is None:
            try:
                # try to get the next one
                self.current_argument = self.arguments.pop(0)
            except IndexError:
                # If we don't have any arguments, left, raise a
                # TooManyArguments error
                raise TooManyArguments(self.tagname, self.todo)
        # parse the current argument and check if this bit was handled by this
        # argument
        handled = self.current_argument.parse(self.parser, bit, self.tagname,
                                              self.kwargs)
        # While this bit is not handled by an argument
        while not handled:
            try:
                # Try to get the next argument
                self.current_argument = self.arguments.pop(0)
            except IndexError:
                # If there is no next argument but there are still breakpoints
                # Raise an exception that we expected a breakpoint
                if self.options.breakpoints:
                    raise BreakpointExpected(self.tagname,
                                             self.options.breakpoints, bit)
                elif self.options.next_breakpoint:
                    raise BreakpointExpected(self.tagname,
                                             [self.options.next_breakpoint],
                                             bit)
                else:
                    # Otherwise raise a TooManyArguments excption
                    raise TooManyArguments(self.tagname, self.todo)
            # Try next argument
            handled = self.current_argument.parse(self.parser, bit,
                                                  self.tagname, self.kwargs)

    def finish(self):
        """
        Finish up parsing by checking all remaining breakpoint scopes
        """
        # Check if there are any required arguments left in the current
        # breakpoint
        self.check_required()
        # While there are still breakpoints left
        while self.options.next_breakpoint:
            # Shift to the next breakpoint
            self.options.shift_breakpoint()
            self.arguments = self.options.get_arguments()
            # And check this breakpoints arguments for required arguments.
            self.check_required()

    def parse_blocks(self):
        """
        Parse template blocks for block tags.

        Example:
            {% a %} b {% c %} d {% e %} f {% g %}
             => pre_c: b
                pre_e: d
                pre_g: f
            {% a %} b {% f %}
             => pre_c: b
                pre_e: None
                pre_g: None
        """
        # if no blocks are defined, bail out
        if not self.options.blocks:
            return
        # copy the blocks
        blocks = deepcopy(self.options.blocks)
        identifiers = {}
        for block in blocks:
            identifiers[block] = block.collect(self)
        while blocks:
            block_identifiers = []
            current_block = blocks.pop(0)
            current_identifiers = identifiers[current_block]
            block_identifiers = list(current_identifiers)
            for block in blocks:
                block_identifiers += identifiers[block]
            nodelist = self.parser.parse(block_identifiers)
            token = self.parser.next_token()
            while token.contents not in current_identifiers:
                empty_block = blocks.pop(0)
                current_identifiers = identifiers[empty_block]
                self.blocks[empty_block.alias] = template.NodeList()
            self.blocks[current_block.alias] = nodelist

    def check_required(self):
        """
        Iterate over arguments, checking if they're required, otherwise
        populating the kwargs dictionary with their defaults.
        """
        for argument in self.arguments:
            if argument.required:
                raise ArgumentRequiredError(argument, self.tagname)
            else:
                self.kwargs[argument.name] = argument.get_default()
