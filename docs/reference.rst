=========
Reference
=========

***************************
:mod:`classytags.arguments`
***************************

.. module:: classytags.arguments

This module contains standard argument types.


.. class:: Argument(name[, default=None][, required=True], [resolve=True])

    A basic single value argument with *name* as it's name.
    
    *default* is used if *required* is False and this argument is not given.
    
    If *resolve* is ``False``, the argument will
    not try to resolve it's contents against the context. This is especially
    useful for 'as varname' arguments. Note that quotation marks around the
    argument will be removed if there are any.
    
    .. attribute:: value_class
    
        The class to be used to wrap the value in. Defaults to
        :class:`classytags.values.StringValue.` 
    
    .. method:: get_default()
    
        Returns the default value for this argument
        
    .. method:: parse(parser, token, tagname, kwargs)
    
        Parses a single *token* into *kwargs*. Should return ``True`` if it
        consumed this token or ``False`` if it didn't.
        
    .. method:: parse_token(parser, token)
    
        Parses a single *token* using *parser* into an object which is can be
        resolved against a context. Usually this is a template variable, a
        filter expression or a :class:`classytags.utils.TemplateConstant`.


.. class:: Argument(name[, default=None][, required=True], [resolve=True])

    Same as :class:`classytags.arguments.Argument` but with
    :class:`classytags.values.StrictStringValue` as :attr:`value_class`.


.. class:: KeywordArgument(name[, default=None][, required=True] \
                          [, resolve=True][, defaultkey=None][, splitter='='])

    An argument that allows ``key=value`` notation.
    
    *defaultkey* is used as key if no key is given or the default value should
    be used.

    *splitter* is used to split the key value pair.
    
    .. attribute:: wrapper_class
    
        Class to use to wrap the key value pair in. Defaults to
        :class:`classytags.values.DictValue`.
    
        
.. class:: IntegerArgument

    Same as :class:`classytags.arguments.Argument` but with
    :class:`classytags.values.IntegerValue` as :attr:`value_class`.
    
    
.. class:: ChoiceArgument(name, choices[, default=None][, required=True] \
                          [, resolve=True])

	An argument which validates it's input against predefined choices.

    
.. class:: MultiValueArgument(name[, default=NULL][, required=True] \
                              [, max_values=None][, resolve=True])

    An argument which accepts a variable amount of values. The maximum amount of
    accepted values can be controlled with the *max_values* argument which 
    defaults to ``None``, meaning there is no maximum amount of values.
    
    *default* is an empty list if *required* is ``False``.
    
    *resolve* has the same effects as in 
    :class:`classytags.arguments.Argument` however applies to all values of this
    argument.
    
    The default value for :attr:`value_class` is$
    :class:`classytags.values.ListValue`.
    
    .. attribute:: sequence_class
    
        Class to be used to build the sequence. Defaults to 
        :class:`classytags.utils.ResolvableList`.


.. class:: MultiKeywordArgument(name[, default=None][, required=True] \
                                [, resolve=True][, max_values=None] \
                                [, splitter='='])

    Similar to :class:`classytags.arguments.KeywordArgument` but allows multiple
    key value pairs to be given. The will be merged into one dictionary.
    
    Arguments are the same as for :class:`classytags.arguments.KeywordArgument`
    and :class:`classytags.arguments.MultiValueArgument`, except that
    *default_key* is not accepted and *default* should be a dictionary or
    ``None``.

  
.. class:: Flag(name[, default=NULL][, true_values=None][, false_values=None] \
                [, case_sensitive=False])
    
    A boolean flag. Either *true_values* or *false_values* must be provided.
    
    If *default* is not given, this argument is required.
    
    *true_values* and *false_values* must be either a list or a tuple of 
    strings. If both *true_values* and *false_values* are given, any value not
    in those sequences will raise a :class:`classytag.exceptions.InvalidFlag`
    exception.
    
    *case_sensitive* defaults to ``False`` and controls whether the values are
    matched case sensitive or not.
    
    
************************
:mod:`classytags.blocks`
************************

.. module:: classytags.blocks

This module contains classes for :ref:`advanced-block-definition`.


.. class:: BlockDefintion(alias, *names)

    A block definition with the given alias and a sequence of names. The members
    of the names sequence must either be strings,
    :class:`classytags.blocks.VariableBlockName` instances or other objects
    implementing at least a :meth:`collect` method compatible with the one of
    :class:`classytags.blocks.VariableBlockName`.
    
    .. attribute:: alias
    
        The alias for this definition to be used in the tag's kwargs.
    
    .. attribute:: names 
    
        Sequence of strings or block name definitions.
    
    .. method:: validate(options)
    
        Validates this definition against an instance of
        :class:`classytags.core.Options` by calling the :meth:`validate` on all
        it's :attr:`names` if such a method is available.
        
    .. method:: collect(parser)
    
        Returns a sequence of strings to be used in the ``parse_until``
        statement. This is a sequence of strings that this block accepts to be
        handled. The parser argument is an instance of
        :class:`classytags.parser.Parser`.


.. class:: VariableBlockName(template, argname)

    A block name definition to be used in
    :class:`classytags.blocks.BlockDefinition` to implement block names that
    depend on the (unresolved) value of an argument. The template argument to
    this class should be a string with the ``value`` string substitution
    placeholder. For example: ``'end_my_block %(value)s'``. The argname argument
    is the name of the argument from which the value should be extracted.
    
    .. method:: validate(options)
        
        Validates that the given argname is actually available on the tag.
        
    .. method:: collect(parser)
    
        Returns the template substitued with the value extracted from the tag.  


**********************
:mod:`classytags.core`
**********************

.. module:: classytags.core

This module contains the core objects to create tags.

        
.. class:: Options(*options, **kwargs)

    Holds the options of a tag. *options* should be a sequence of 
    :class:`classytags.arguments.Argument` subclasses or strings (for
    breakpoints).
    You can give they keyword argument *blocks* to define a list of blocks to
    parse until.
    You can specify a custom argument parser by providing the keyword argument
    *parser_class*.
    
    .. attribute:: all_argument_names
    
        A list of all argument names in this tag options.
        Used by :class:`classytags.blocks.VariableBlockName` to validate it's
        definition. 
    
    .. method:: get_parser_class()
    
        Returns :class:`classytags.parser.Parser` or a subclass of it.
        
    .. method:: bootstrap()
        
        An internal method to bootstrap the arguments. Returns an instance of
        :class:`classytags.utils.StructuredOptions`.
        
    .. method:: parse(parser, token):
        
        An internal method to parse the template tag. Returns a tuple
        ``(arguments, blocks)``.


.. class:: TagMeta

    The metaclass of :class:`classytags.core.Tag` which ensures the tag has a
    name attribute by setting one based on the classes name if none is provided.

   
.. class:: Tag(parser, token)

    The ``Tag`` class is nothing other than a subclass of
    :class:`django.template.Node` which handles argument parsing in it's 
    :meth:`__init__` method rather than an external function. In a normal use
    case you should only override :attr:`name`, :attr:`options` and
    :meth:`render_tag`.
    
    .. note::
    
        When registering your template tag, register the class object, *not*
        an instance of it.
        
    .. attribute:: name
        
        The name of this tag (for use in templates). This attribute is optional
        and if not provided, the un-camelcase class name will be used instead.
        So MyTag becomes my_tag.
        
    .. attribute:: options
    
        An instance of :class:`classytags.core.Options` which holds the
        options of this tag.
        
    .. method:: __init__(parser, token):
    
        .. warning::
        
            This is an internal method. It is only documented here for those
            who would like to extend django-classy-tags.
            
        This is where the arguments to this tag get parsed. It's the equivalent
        to a *compile function* in Django's standard templating system.
        This method does nothing else but assing the :attr:`kwargs` and 
        :attr:`blocks` attributes to the output of :meth:`options.parse` with
        the given *parser* and *token*.
        
    .. method:: render(context)
    
        .. warning::
        
            This is an internal method. It is only documented here for those
            who would like to extend django-classy-tags.
            
        This method resolves the arguments to this tag against the context and
        then calls :meth:`render_tag` with the context and those arguments and
        returns the return value of that method.
        
    .. method:: render_tag(context[, **kwargs])
    
        The method used to render this tag for a given context. *kwargs* is a 
        dictionary of the (already resolved) options of this tag as well as the
        blocks (as nodelists) this tag parses until if any are given.
        This method should return a string.
    

****************************
:mod:`classytags.exceptions`
****************************

.. module:: classytags.exceptions

This module contains the custom exceptions used by django-classy-tags.
 
.. exception:: BaseError
    
    The base class for all custom excpetions, should never be raised directly.
    

.. exception:: ArgumentRequiredError(argument, tagname)

    Gets raised if an option of a tag is required but not provided.
    

.. exception:: InvalidFlag(argname, actual_value, allowed_values, tagname)

    Gets raised if a given value for a flag option is neither in *true_values*
    nor *false_values*.
    

.. exception:: BreakpointExpected(tagname, breakpoints, got)

    Gets raised if a breakpoint was expected, but another argument was found.
    

.. exception:: TooManyArguments(tagname, extra)

    Gets raised if too many arguments are provided for a tag.
        
        
*************************
:mod:`classytags.helpers`
*************************

.. module:: classytags.helpers

This modules contains helper classes to make building template tags even easier.

.. class:: AsTag

    A helper tag base class to build 'as varname' tags. Note that the option
    class still has to contain the 'as varname' information. This tag will use
    the last argument in the options class to set the value into the context.
    
    This class implements the method :meth:`classytags.helpers.AsTag.get_value`
    which gets the context and all arguments except for the varname argument as
    arguments. It should always return the value this tag comes up with, the
    class then takes care of either putting the value into the context or 
    returns it if the varname argument is not provided.
    
    .. note::
    
        You should not override the :meth:`render_tag` method of this class.

    .. method:: get_value_for_context(context, **kwargs):

        .. versionadded:: 0.5 

        Should return the value of this tag if used in the 'as varname' form.
        By default this method just calls ``get_value`` and returns that.

        You may want to use this method if you want to suppress exceptions in
        the 'as varname' case.
    
    .. method:: get_value(context, **kwargs)
    
        Should return the value of this tag. The context setting is done in the
        :meth:`classytags.core.Tag.render_tag` method of this class.
        
        
.. class:: InclusionTag

    A helper class for writing inclusion tags (template tags which render a
    template).
    
    .. note::
    
        You should not override the :meth:`render_tag` method of this class.
        
    .. attribute:: template
    
        The template to use if :meth:`get_template` is not overridden.
    
    .. attribute:: push_context

        .. versionadded:: 0.5.2
    
        By default, this is ``False``. If it's set to ``True`` the context will
        be pushed before rendering the included template, preventing context
        pollution.
        
    .. method:: get_template(context, **kwargs)
    
        This method should return a template (path) for this context and
        arguments. By default returns the value of :attr:`template`.
        
    .. method:: get_context(context, **kwargs)
    
        Should return the context (as a dictionary or an instance of 
        :class:`django.template.Context` or a subclass of it) to use to render
        the template. By default returns an empty dictionary.


************************
:mod:`classytags.parser`
************************

.. module:: classytags.parser

The default argument parser lies here.


.. class:: Parser(options)

    The default argument parser class. It get's initialized with an instance of
    :class:`classytags.utils.StructuredOptions`.
    
    .. attribute:: options
    
        The :class:`classytags.utils.StructuredOptions` instance given when the
        parser was instantiated. 
    
    .. attribute:: parser
    
        The (template) parser used to parse this tag.
        
    .. attribute:: bits
    
        The split tokens.
        
    .. attribute:: tagname
    
        Name of this tag.
        
    .. attribute:: kwargs
    
        The data extracted from the bits.
        
    .. attribute:: blocks
    
        A dictionary holding the block nodelists.
        
    .. attribute:: arguments
        
        The arguments in the current breakpoint scope.
        
    .. attribute:: current_argument
    
        The current argument if any.
        
    .. attribute:: todo
    
        Remaining bits. Used for more helpful exception messages. 

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
        
        The current bit is an argument. Handle it and contribute to
        :attr:`kwargs`.
        
    .. method:: parse_blocks()
    
        Parses the blocks this tag wants to parse until if any are provided.
        
    .. method:: finish()
    
        After all bits have been parsed, finish all remaining breakpoint scopes.
        
    .. method:: check_required()
    
        A helper method to check if there's any required arguments left in the
        current breakpoint scope. Raises a
        :exc:`classytags.exceptions.ArgumentRequiredError` if one is found and
        contributes all optional arguments to :attr:`kwargs`.


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
    
    .. attribute:: literal
    
        Used by the :class:`classytags.blocks.VariableBlockName` to generate
        it's final name.
    

.. class:: StructuredOptions(options, breakpoints)

    A helper class to organize options.
    
    .. attribute:: options
    
        The arguments in this options.
        
    .. attribute:: breakpoints
        
        A *copy* of the breakpoints in this options
        
    .. attribute:: blocks
    
        A *copy* of the list of tuples (blockname, alias) of blocks of this tag.  
        
    .. attribute:: current_breakpoint
    
        The current breakpoint.
        
    .. attribute:: next_breakpoint
    
        The next breakpoint (if there is any).
    
    .. method:: shift_breakpoint()
    
        Shift to the next breakpoint and update :attr:`current_breakpoint` and
        :attr:`next_breakpoint`.
        
    .. method:: get_arguments()
    
        Returns a copy of the arguments in the current breakpoint scope.


.. class:: ResolvableList(item)

    A subclass of list which resolves all it's items against a context when it's
    resolve method gets called.


.. function:: get_default_name(name)

    Turns 'CamelCase' into 'camel_case'.


************************
:mod:`classytags.values`
************************

.. module:: classytags.values

.. class:: StringValue(var)

    .. attribute:: errors
        
        A dictionary holding error messages which can be caused by this value
        class. Defaults to an empty dictionary.
        
    .. attribute:: value_on_error
    
        The value to use when the validation of a input value fails in non-debug
        mode. Defaults to an empty string.
        
    .. attribute:: var
    
        The variable wrapped by this value instance.
        
    .. method:: resolve(context)
    
        Resolve :attr:`var` against *context* and validate it by calling the 
        :meth:`clean` method with the resolved value.
        
    .. method:: clean(value)
    
        Validates and/or cleans a resolved value. This method should always
        return something. If validation fails, the :meth:`error` helper method
        should be used to properly handle debug modes.
        
    .. method:: error(value, category)
    
        Handles an error in *category* caused by *value*. In debug mode this
        will cause a :exc:`django.template.TemplateSyntaxError` to be raised,
        otherwise a `TemplateSyntaxWarning` is called and
        :attr:`value_on_error` is returned.
        The message to be used for both the exception and the warning will be
        constructed by the message in :attr:`errors` if *category* is in it. The
        value can be used as a named string formatting parameter.


.. class:: StrictStringValue(var)

    Same as :class:`StringValue` but enforces that the value passed to it is a
    string (instance of ``basestring``).
        
.. class:: IntegerValue(var)

    Subclass of :class:`StringValue`.

    .. method:: clean(value)
    
        Tries to convert the value to an integer.
        
        
.. class:: ListValue(value)

    Subclass of :class:`StringValue` and :class:`list`.
    
    Appends the initial value to itself in initialization.
    
    .. method:: resolve(context)
    
        Resolves all items in itself against *context* and calls :meth:`clean`
        with the list of resolved values.


.. class:: DictValue(dict)

    Subclass of :class:`StringValue` and :class:`dict`.
    
    .. method:: resolve(context)
        
        Resolves all *values* against *context* and calls :meth:`clean` with the 
        resolved dictionary.
