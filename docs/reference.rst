=========
Reference
=========

***************************
:mod:`classytags.arguments`
***************************

.. module:: classytags.arguments

This module contains standard argument types.

.. class:: Argument(name[, default][, required], [no_resolve])

    A basic single value argument with *name* as it's name.
    
    *default* is used if *required* is False and this argument is not given. It
    defaults to ``None``.
    
    *required* defaults to ``True``.
    
    If *no_resolve* is ``True`` (it defaults to ``False``), the argument will
    not try to resolve it's contents against the context. This is especially
    useful for 'as varname' arguments. Note that quotation marks around the
    argument will be removed if there are any.
    
    .. method:: get_default
    
        Returns the default value for this argument
        
    .. method:: parse(parser, token, tagname, kwargs)
    
        Parses a single *token* into *kwargs*. Should return ``True`` if it
        consumed this token or ``False`` if it didn't.
        
    .. method:: parse_token(parser, token)
    
        Parses a single *token* using *parser* into an object which is can be
        resolved against a context. Usually this is a template variable, a
        filter expression or a :class:`classytags.utils.TemplateConstant`.

    
.. class:: MultiValueArgument(self, name[, default][, required][, max_values][, no_resolve])

    An argument which accepts a variable amount of values. The maximum amount of
    accepted values can be controlled with the *max_values* argument which 
    defaults to ``None``, meaning there is no maximum amount of values.
    
    *default* is an empty list if *required* is ``False``.
    
    *no_resolve* has the same effects as in 
    :class:`classytags.arguments.Argument` however applies to all values of this
    argument.

    
.. class:: Flag(name[, default][, true_values][, false_values][, case_sensitive])
    
    A boolean flag. Either *true_values* or *false_values* must be provided.
    
    If *default* is not given, this argument is required.
    
    *true_values* and *false_values* must be either a list or a tuple of 
    strings. If both *true_values* and *false_values* are given, any value not
    in those sequences will raise a :class:`classytag.exceptions.InvalidFlag`
    exception.
    
    *case_sensitive* defaults to ``False`` and controls whether the values are
    matched case sensitive or not.


**********************
:mod:`classytags.core`
**********************

.. module:: classytags.core

This module contains the core objects to create tags.

.. class:: Tag(parser, token)

    .. note::
    
        You should never have to manually initialize this class and you should
        not overwrite it's ``__init__`` method.
        
    .. attribute:: name
        
        The name of this tag (for use in templates). This attribute is optional
        and if not provided, the un-camelcase class name will be used instead.
        So MyTag becomes my_tag.
        
    .. attribute:: options
    
        An instance of :class:`classytags.core.Options` which holds the
        options of this tag.
        
    .. method:: render_tag(context[, **kwargs])
    
        The method used to render this tag for a given context. *kwargs* is a 
        dictionary of the (already resolved) options of this tag.
        This method should return a string.

        
.. class:: Options(*options)

    Holds the options of a tag. *options* should be a sequence of 
    :class:`classytags.arguments.Argument` subclasses or strings (for
    breakpoints).
    You can specify a custom argument parser by subclassing this class and 
    changing :meth:`classytags.core.Options.get_parser_class`.
    
    .. method:: get_parser_class()
    
        Should return :class:`classytags.parser.Parser` or a subclass of it. Use
        this method to define a custom parser class.
        
    .. method:: bootstrap()
        
        An internal method to bootstrap the arguments.
        
    .. method:: parse(parser, token):
        
        An internal method to parse the template tag.
    

****************************
:mod:`classytags.exceptions`
****************************

.. module:: classytags.exceptions

This module contains the custom exceptions used by django-classy-tags.
 
.. class:: BaseError
    
    The base class for all custom excpetions, should never be raised directly.
    

.. class:: ArgumentRequiredError(argument, tagname)

    Gets raised if an option of a tag is required but not provided.
    

.. class:: InvalidFlag(argname, actual_value, allowed_values, tagname)

    Gets raised if a given value for a flag option is neither in *true_values*
    nor *false_values*.
    

.. class:: BreakpointExpected(tagname, breakpoints, got)

    Gets raised if a breakpoint was expected, but another argument was found.
    

.. class:: TooManyArguments(tagname, extra)

    Gets raised if too many arguments are provided for a tag.


***********************
:mod:`classytags.utils`
***********************

.. module:: classytags.utils

Utility classes and methods for django-classy-tags.

.. class:: NULL

    A pseudo type.


.. class:: TemplateConstant(value)
    
    A constant pseudo template variable which always returns it's initial value
    when resolved.
    

.. class:: StructuredOptions(options, breakpoints)

    A helper class to organize options.


.. class:: ResolvableList(item)

    A subclass of list which resolves all it's items against a context when it's
    resolve method gets called.
    
.. function:: get_default_name(name)

    Turns 'CamelCase' into 'camel_case'


************************
:mod:`classytags.parser`
************************

.. module:: classytags.parser

The default argument parser lies here.


.. class:: Parser(options)

    The default argument parser class. 

.. method:: parse(parser, token)
    
    Parses a token stream. This is called when your template tag is parsed.

.. method:: handle_bit(bit)
    
    Handle the current bit (token).

.. method:: handle_next_breakpoint(bit)

    The current bit is the next breakpoint. Make sure the current scope can be
    finished successfully and shift to the next one.

.. method:: handle_breakpoints(bit)

    The current bit is a future breakpoint, try to close all breakpoint scopes
    before that breakpoint and shift to it.

.. method:: handle_argument(bit)
    
    The current bit is an argument. Handle it and contribute to *self.kwargs*
    
.. method:: finish

    After all bits have been parsed, finish all remaining breakpoint scopes.
    
.. check_required

    A helper method to check if there's any required arguments left in the
    current breakpoint scope. Raises a
    :class:`classytags.exceptions.ArgumentRequiredError` if one is found and
    contributes all optional arguments to *self.kwargs*.