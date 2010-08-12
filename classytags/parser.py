from classytags.exceptions import BreakpointExpected, TooManyArguments, \
    ArgumentRequiredError


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
        self.arguments = self.options.get_arguments()
        self.current_argument = None
        self.todo = list(self.bits)
        for bit in self.bits:
            self.handle_bit(bit)
        self.finish()
        return self.kwargs

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
        self.check_required()
        self.options.shift_breakpoint()
        self.arguments = self.options.get_arguments()
        self.current_argument = self.arguments.pop(0)
        
    def handle_breakpoints(self, bit):
        """
        Handle a bit which is a future breakpoint by trying to finish all 
        intermediate breakpoint codes as well as the current scope and then
        shift.
        """
        while bit != self.options.current_breakpoint:
            self.check_required()
            self.options.shift_breakpoint()
            self.arguments = self.options.get_arguments()
        self.current_argument = self.arguments.pop(0)
        
    def handle_argument(self, bit):
        """
        Handle the current argument.
        """
        if self.current_argument is None:
            self.current_argument = self.arguments.pop(0)
        handled = self.current_argument.parse(self.parser, bit, self.tagname, self.kwargs)
        while not handled:
            try:
                self.current_argument = self.arguments.pop(0)
            except IndexError:
                if self.options.breakpoints:
                    raise BreakpointExpected(self.tagname, self.options.breakpoints, bit)
                elif self.options.next_breakpoint:
                    raise BreakpointExpected(self.tagname, [self.options.next_breakpoint], bit)
                else:
                    raise TooManyArguments(self.tagname, self.todo)
            handled = self.current_argument.parse(self.parser, bit, self.tagname, self.kwargs)
            
    def finish(self):
        """
        Finish up parsing by checking all remaining breakpoint scopes
        """
        self.check_required()
        while self.options.next_breakpoint:
            self.options.shift_breakpoint()
            self.arguments = self.options.get_arguments()
            self.check_required()
    
    def check_required(self):
        """
        Iterate over arguments, checking if they're required, otherwise populating
        the kwargs dictionary with their defaults.
        """
        for argument in self.arguments:
            if argument.required:
                raise ArgumentRequiredError(argument, self.tagname)
            else:
                self.kwargs[argument.name] = argument.get_default()