.. django-classy-tags documentation master file, created by
   sphinx-quickstart on Mon Aug  9 21:31:48 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-classy-tags's documentation!
==============================================

django-classy-tags is an approach at making writing template tags in Django
easier, shorter and more fun by providing an extensible argument parser which
reduces most of the boiler plate code you usually have to write when coding
custom template tags.

django-classy-tags does **no magic by design**. Thus you will not get automatic 
registering/loading of your tags like other solutions provide. You will not get
automatic argument guessing from function signatures but rather you have to
declare what arguments your tag accepts. There is also no magic in your template
tag class either, it's just a subclass of :class:`django.template.Node` which
invokes a parser class to parse the arguments when it's initialized and resolves
those arguments into keyword arguments in it's ``render`` method and calls it's
``render_tag`` method with those keyword arguments.

Contents:

.. toctree::
    :maxdepth: 2
    
    installation
    usage
    reference
    extend

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

