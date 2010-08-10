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

.. class:: Tag

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
    

****************************
:mod:`classytags.exceptions`
****************************

.. module:: classytags.exceptions

This module contains the custom exceptions used by django-classy-tags.
 
.. class:: BaseError
    
    The base class for all custom excpetions, should never be raised directly.
    

.. class:: ArgumentRequiredError

    Gets raised if an option of a tag is required but not provided.
    

.. class:: InvalidFlag

    Gets raised if a given value for a flag option is neither in *true_values*
    nor *false_values*.
    

.. class:: BreakpointExpected

    Gets raised if a breakpoint was expected, but another argument was found.
    

.. class:: TooManyArguments

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
    

.. class:: StructuredOptions

    A helper class to organize options.


.. class:: ResolvableList

    A subclass of list which resolves all it's items against a context when it's
    resolve method gets called.