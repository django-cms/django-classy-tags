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
        __name__ = 'hello_world'
        
        def render_tag(self, context):
            return 'hello world'
            
    register.tag(HelloWorld)
        

Now let's explain this. To create a tag, you subclass ``classytags.core.Tag``
and define a ``render_tag`` method which takes the context and any template tag
options you define as arguments to the method. Since we did not define any
options for this tag, it only takes context. The ``render_tag`` method should
always return a string.

``__name___`` on a tag class is what is used when registering the tag with a
Django template tag library and also what will be used in the template. 

****************
Defining options
****************

Defining options is done by setting the ``options`` attribute on your tag class
to an instance of ``classytags.core.Options``. The ``Options`` class takes any
amount of argument objects or strings (called breakpoints) as initialization
arguments.

Let's build a tag which takes a single argument and an optional 'as varname'
argument::

    from classytags.core import Tag, Options
    from classytags.arguments import Argument
    
    class Hello(Tag):
        __name__ = 'hello'
        options = Options(
            Argument('name'),
            'as',
            Argument('varname', required=False)
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