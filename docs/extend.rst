============================
Extending django-classy-tags
============================

You can extend django-classy-tags by writing your own subclasses of
:class:`classytags.arguments.Argument` which behave to your needs. If that does
not cover your needs, you may also subclass :class:`classytags.core.Options` and
set a custom argument parser, which should subclass
:class:`classytags.parser.Parser`.

********************************
Creating a custom argument class
********************************

The most important method in this class for customization is
:meth:`classytags.arguments.Argument.parse`, so let's have a closer look at it.
It takes exactly four arguments, which are as follows:

* *parser*: An instance of :class:`django.template.Parser`.
* *token*: The current token as a string.
* *tagname*: The name of the tag being handled.
* *kwargs*: The dictionary of already parsed arguments.

The parse method must return a boolean value:

* If your method returns ``True``, it means it has successfully handled the
  provided token. Your method has to add content to *kwargs* itself. The parser
  does not do that! When you return ``True``, the next token will also try to
  get parsed by this argument's parse method.
* If your method returns ``False``, it means it has not handled this token and
  the next argument class in the stack should be used to handle this token.
  Usually you would return ``False`` when your argument's name is already in
  *kwargs*. Obviously this only applies to single-value arguments.

So let's look at the standard :meth:`classytags.arguments.Argument.parse`::

    def parse(self, parser, token, tagname, kwargs):
        """
        Parse a token.
        """
        if self.name in kwargs:
            return False
        else:
            kwargs[self.name] = self.parse_token(parser, token)
            return True

First it checks if the name is already in *kwargs*. If so, return ``False`` and
let the next argument handle this token. Otherwise do some checking if we should
resolve this token or not and add it to *kwargs*. Finally return ``True``.

You might notice the :meth:`classytags.arguments.Argument.parse_token` method
used there. This method is responsible for turning an token into a template
variable, a filter expression or any other object which allows to be resolved
against a context. The one in :class:`classytags.arguments.Argument` looks like
this::

    def parse_token(self, parser, token):
        if self.resolve:
            return parser.compile_filter(token)
        else:
            return TemplateConstant(token)


Cleaning arguments
------------------

If all you want to do is clean arguments or enforce a certain type, you can
just change the :attr:`classytags.arguments.Argument.value_class` of your
subclass of :class:`classytags.arguments.Argument` to a subclass of
:class:`classytags.values.StringValue` which implements a `clean` method in
which you can check the type and/or cast a type on the value. For further
information on value classes, see :mod:`classytags.values`.


**********************
Custom argument parser
**********************

The argument parser was written with extensibility in mind. All important steps
are split into individual methods which can be overwritten. For information
about those methods, please refer to the reference about
:class:`classytags.parser.Parser`.

To use a custom parser, provide it as the ``parser_class`` keyword argument to
:class:`classytags.core.Options`.

.. note::

    Each time your tag gets parsed, a new instance of the parser class gets
    created. This makes it safe to use ``self``.


*******
Example
*******

Let's make an argument which, when resolved, returns a template.

First we need a helper class which, after resolving loads the template specified
by the value::

    from django.template.loader import get_template

    class TemplateResolver:
        def __init__(self, real):
            self.real = real

        def resolve(self, context):
            value = self.real.resolve(context)
            return get_template(value)


Now for the real argument::

    from classytags.arguments import Argument

    class TemplateArgument(Argument):
        def parse_token(self, parser, token):
            real = super().parse_token(parser, token)
            return TemplateResolver(real)
