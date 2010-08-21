=====
Usage
=====

****************
A simple example
****************

A very basic tag which takes no arguments and always returns ``'hello world'`` 
would be::

    from classytags.core import Tag
    from django import template
    
    register = template.Library()
    
    class HelloWorld(Tag):
        name = 'hello_world'
        
        def render_tag(self, context):
            return 'hello world'
            
    register.tag(HelloWorld)
        

Now let's explain this. To create a tag, you subclass :class:`classytags.core.Tag`
and define a :meth:`classytags.core.Tag.render_tag` method which takes the
context and any template tag options you define as arguments to the method.
Since we did not define any options for this tag, it only takes context. The 
:meth:`classytags.core.Tag.render_tag` method should always return a string.

:attr:`classytags.core.Tag.render_tag` on a tag class is what is used when 
registering the tag with a Django template tag library and also what will be
used in the template. 

****************
Defining options
****************

Defining options is done by setting the :attr:`classytags.core.Tag.options`
attribute on your tag class to an instance of :class:`classytags.core.Options`.
The ``Options`` class takes any amount of argument objects or strings (called 
breakpoints) as initialization arguments.

Let's build a tag which takes a single argument and an optional 'as varname'
argument::

    from classytags.core import Tag, Options
    from classytags.arguments import Argument
    from django import template
    
    register = template.Library()
    
    class Hello(Tag):
        name = 'hello'
        options = Options(
            Argument('name'),
            'as',
            Argument('varname', required=False, resolve=False)
        )
        
        def render_tag(self, context, name, varname):
            output = 'hello %s' % name
            if varname:
                context[varname] = output
                return ''
            else:
                return output
            
    register.tag(Hello)
    
In a template we could now do either ``{% hello "world" %}`` which would output
``'hello world'`` or ``{% hello "world" as "varname" %}`` which would output
nothing but set the ``{{ varname }}`` template variable to ``'hello world'``.
You may also use ``{% hello "world" as varname %}`` to achieve the same result
like the last example.

*******************
Writing a block tag
*******************

You can write tags which wrap a block (nodelist) in the template. An example for
this kind of tag is Django's built-in ``{% with %}`` tag.

To write the ``{% with %}`` tag from Django using django-classy-tags you would
do::

    from classytags.core import Tag, Options
    from classytags.arguments import Argument
    from django import template
    
    register = template.Library()
    
    class With(Tag):
        name = 'with'
        options = Options(
            Argument('variable'),
            'as',
            Argument('varname', resolve=False),
            blocks=[('endwith', 'nodelist')],
        )
        
        def render_tag(self, context, variable, varname, nodelist):
            context.push()
            context[varname] = variable
            output = nodelist.render(context)
            context.pop()
            return output 
            
    register.tag(With)
    

Working with multiple blocks
----------------------------

If you're working with multiple, optional blocks, the nodelist is always
credited to the leftmost block name.

For example the Django ``for`` tag accepts an optional ``empty`` block. Let's
take following classytag options::
    
    options = Options(
        CommaSeperatableMultiValueArgument('loopvars'),
        'in',
        arguments.Argument('values'),
        blocks=[('empty', 'pre_empty'), ('endfor', 'post_empty')],
    )
    
If you use it with ``{% for x in y %}hello{% empty %}world{% enfor %}`` the
*pre_empty* argument to your :meth:`classytags.arguments.Argument.render_tag``
would hold a nodelist containing ``hello``, *post_empty* would contain
``world``. Now if you have ``{% for x in y%}{{ hello }}{% endfor %}``,
*pre_empty* remains the same, but *post_empty* is an empty nodelist.


************
Easy as-Tags
************

There is a helper class for tags which store their output (optionally) in the
context. This class is in :class:`classytags.helpers.AsTag` and instead of
defining a `render_tag`method, you define a
:meth:`classytags.helpers.AsTag.get_value` method which returns the value you
want to either display or be put into the context.

Here is a small example::


    from classytags.core import Options
    from classytags.arguments import Argument
    from classytags.helpers import AsTag
    from django import template
    
    register = template.Library()

    class Dummy(AsTag):
        options = Options(
            'as',
            Argument('varname', resolve=False, required=False),
        )
        
        def get_value(self, context):
            return 'dummy'
            
    register.tag(Dummy)
    
Now if you do ``{% dummy %}`` in your templates, it will output 'dummy' there.
If you use ``{% dummy as myvar %}`` 'dummy' will be stored into the ``myvar``
context variable.