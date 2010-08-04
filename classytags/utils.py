from copy import copy

class NULL:
    """
    Internal type to differentiate between None and No-Input
    """


class TemplateConstant(object):
    """
    A 'constant' internal template variable which basically allows 'resolving'
    returning it's initial value
    """
    def __init__(self, value):
        self.value = value
        
    def __repr__(self):
        return '<TemplateConstant: %s>' % repr(self.value) 
        
    def resolve(self, context):
        return self.value
    
    
class StructuredOptions(object):
    """
    Bootstrapped options
    """
    def __init__(self, options, breakpoints):
        self.options = options
        self.breakpoints = copy(breakpoints)
        self.current_breakpoint = None
        if self.breakpoints:
            self.next_breakpoint = self.breakpoints.pop(0)
        else:
            self.next_breakpoint = None
            
    def shift_breakpoint(self):
        """
        Shift to the next breakpoint
        """
        self.current_breakpoint = self.next_breakpoint
        if self.breakpoints:
            self.next_breakpoint = self.breakpoints.pop(0)
        else:
            self.next_breakpoint = None
            
    def get_arguments(self):
        """
        Get the current arguments
        """
        return copy(self.options[self.current_breakpoint])


class ResolvableList(list):
    """
    A list of template variables for easy resolving
    """
    def __init__(self, item):
        super(ResolvableList, self).__init__()
        self.append(item)
        
    def resolve(self, context):
        return [item.resolve(context) for item in self]
    
    def __repr__(self):
        return '<ResolvableList: %s>' % super(ResolvableList, self).__repr__()