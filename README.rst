==================
django-classy-tags
==================

Please refer to the documentation in the docs/ directory for help. For a HTML
rendered version of it please see `here <http://django-classy-tags.rtfd.org>`_.

******************
About this project
******************

The goal of this project is to create a new way of writing Django template tags
which is fully compatible with the current Django templating infrastructure.
This new way should be easy, clean and require as little boilerplate code as
possible while still staying as powerful as possible.

Features
--------

* Class based template tags.
* Template tag argument parser.
* Declarative way to define arguments.
* Supports (theoretically infinite) parse-until blocks.
* Extensible!


*****************
For the impatient
*****************

This is how a tag looks like using django-classy-tags::

    from classytags.core import Tag, Options
    from classytags.arguments import Argument
    from django import template
    
    register = template.Library()
    
    class Hello(Tag):
        options = Options(
            Argument('name', required=False, default='world'),
            'as',
            Argument('varname', required=False, resolve=False)
        )
        
        def render_tag(self, context, name, varname):
            output = 'hello %s' % name
            if varname:
                context[varname] = output
                return ''
            return output
            
    register.tag(Hello)
            
That's your standard *hello world* example. Which can be used like this:

* ``{% hello %}``: Outputs ``hello world``
* ``{% hello "classytags" %}``: Outputs ``hello classytags``
* ``{% hello as myvar %}``: Outputs nothing but stores ``hello world`` into the
  template variable ``myvar``.
* ``{% hello "my friend" as othervar %}``: Outputs nothing but stores 
  ``hello my friend`` into the template variable ``othervar``.
