============================
Extending django-classy-tags
============================

You can extend django-classy-tags by writing your own subclasses of
:class:`classytags.arguments.Argument` which behave to your needs. There is one
method on that class which does all the action:
:meth:`classytags.arguments.Argument.parse`. The ``__init__`` method is just
used to provide configuration for this argument.

So let's have a close look at this :meth:`classytags.arguments.Argument.parse`
method. It takes exactly 4 arguments:

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
        if self.no_resolve:
            return TemplateConstant(token)
        else:
            return parser.compile_filter(token)

*******
Example
*******

Let's make an argument which, when resolved, returns a template.

First we need a helper class which, after resolving loads the template specified
by the value::

    from django.template.loader import get_template

    class TemplateResolver(object):
        def __init__(self, real):
            self.real = real
            
        def resolve(self, context):
            value = self.real.resolve(context)
            return get_template(value)
            
            
Now for the real argument::

    from classytags.arguments import Argument
    
    class TemplateArgument(Argument):
        def parse_token(self, parser, token):
            real = super(TemplateArgument, self).parse_token(parser, token)
            return TemplateResolver(real)