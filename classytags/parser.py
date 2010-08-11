from classytags.exceptions import *


def check_required(arguments, tagname, kwargs):
    """
    Iterate over arguments, checking if they're required, otherwise populating
    the kwargs dictionary with their defaults.
    """
    for argument in arguments:
        if argument.required:
            raise ArgumentRequiredError(argument, tagname)
        else:
            kwargs[argument.name] = argument.get_default()


class Parser(object):
    """
    Argument parsing class
    """
    debug = False
    def __init__(self, options):
        self.options = options
        
    def parse(self, parser, tokens):
        """
        Parse a token stream
        """
        bits = tokens.split_contents()
        tagname = bits.pop(0)
        options = self.options.bootstrap()
        kwargs = {}
        arguments = options.get_arguments()
        current_argument = None
        todo = list(bits)
        for bit in bits:
            self.dbg("current bit is '%s'" % bit)
            if bit == options.next_breakpoint:
                self.dbg("this is the next breakpoint")
                check_required(arguments, tagname, kwargs)
                self.dbg("finished current breakpoint")
                options.shift_breakpoint()
                self.dbg("shifted to next breakpoint")
                arguments = options.get_arguments()
                self.dbg("got new arguments: %s" % arguments)
                current_argument = arguments.pop(0)
                self.dbg("current argument is now '%s'" % current_argument)
            elif bit in options.breakpoints:
                self.dbg("current bit is a breakpoint")
                while bit != options.current_breakpoint:
                    self.dbg("current bit is not yet the current breakpoint")
                    check_required(arguments, tagname, kwargs)
                    self.dbg("checked remaining arguments for '%s'" % options.current_breakpoint)
                    options.shift_breakpoint()
                    self.dbg("shifted to next breakpoint")
                    arguments = options.get_arguments()
                    self.dbg("got new arguments: %s" % arguments)
                current_argument = arguments.pop(0)
                self.dbg("current argument is now '%s'" % current_argument)
            else:
                if current_argument is None:
                    current_argument = arguments.pop(0)
                    self.dbg("current argument is now '%s'" % current_argument)
                self.dbg("bit is an argument")
                handled = current_argument.parse(parser, bit, tagname, kwargs)
                while not handled:
                    self.dbg("bit was not handled by this argument")
                    try:
                        current_argument = arguments.pop(0)
                    except IndexError:
                        if options.breakpoints:
                            raise BreakpointExpected(tagname, options.breakpoints, bit)
                        elif options.next_breakpoint:
                            raise BreakpointExpected(tagname, [options.breakpoints], bit)
                        else:
                            raise TooManyArguments(tagname, todo)
                    self.dbg("current argument is now '%s'" % current_argument)
                    handled = current_argument.parse(parser, bit, tagname, kwargs)
                self.dbg('bit handled')
            del todo[0]
        self.dbg('no more bits')
        check_required(arguments, tagname, kwargs)
        self.dbg('checked remaining arguments in this breakpoint')
        while options.next_breakpoint:            
            options.shift_breakpoint()
            self.dbg("shifted to next breakpoint")
            arguments = options.get_arguments()
            self.dbg("got new arguments")
            check_required(arguments, tagname, kwargs)
            self.dbg("checked remaining arguments for '%s'" % options.current_breakpoint)
        self.dbg("result: %s" % kwargs)
        return kwargs
    
    def dbg(self, msg):
        """
        Debug wrapper
        """
        if self.debug: # pragma: no cover
            print msg