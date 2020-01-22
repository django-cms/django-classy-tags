
==================
Django Classy Tags
==================

|pypi| |build| |coverage|

The goal of this project is to create a new way of writing Django template tags
which is fully compatible with the current Django templating infrastructure.
This new way should be easy, clean and require as little boilerplate code as
possible while still staying as powerful as possible. Some features:

* Class based template tags.
* Template tag argument parser.
* Declarative way to define arguments.
* Supports (theoretically infinite) parse-until blocks.
* Extensible!


Contributing
============

This is a an open-source project. We'll be delighted to receive your
feedback in the form of issues and pull requests. Before submitting your
pull request, please review our `contribution guidelines
<http://docs.django-cms.org/en/latest/contributing/index.html>`_.

We're grateful to all contributors who have helped create and maintain this package.
Contributors are listed at the `contributors <https://github.com/divio/django-classy-tags/graphs/contributors>`_
section.


Documentation
=============

See ``REQUIREMENTS`` in the `setup.py <https://github.com/divio/django-classy-tags/blob/master/setup.py>`_
file for additional dependencies:

|python| |django|

Please refer to the documentation in the docs/ directory for more information or visit our
`online documentation <https://django-classy-tags.readthedocs.io>`_.


Example
-------

This is how a tag looks like using django-classy-tags:

.. code-block:: python

    from classytags.core import Options
    from classytags.helpers import AsTag
    from classytags.arguments import Argument
    from django import template

    register = template.Library()

    class Hello(AsTag):
        options = Options(
            Argument('name', required=False, default='world'),
            'as',
            Argument('varname', required=False, resolve=False)
        )

        def get_value(self, context, name):
            return 'hello %s' % name

    register.tag(Hello)

That's your standard *hello world* example. Which can be used like this:

* ``{% hello %}``: Outputs ``hello world``
* ``{% hello "classytags" %}``: Outputs ``hello classytags``
* ``{% hello as myvar %}``: Outputs nothing but stores ``hello world`` into the
  template variable ``myvar``.
* ``{% hello "my friend" as othervar %}``: Outputs nothing but stores
  ``hello my friend`` into the template variable ``othervar``.


Running Tests
-------------

You can run tests by executing::

    virtualenv env
    source env/bin/activate
    pip install -r tests/requirements.txt
    python setup.py test


.. |pypi| image:: https://badge.fury.io/py/django-classy-tags.svg
    :target: http://badge.fury.io/py/django-classy-tags
.. |build| image:: https://travis-ci.org/divio/django-classy-tags.svg?branch=master
    :target: https://travis-ci.org/divio/django-classy-tags
.. |coverage| image:: https://codecov.io/gh/divio/django-classy-tags/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/divio/django-classy-tags

.. |python| image:: https://img.shields.io/badge/python-2.7%20%7C%203.4+-blue.svg
    :target: https://pypi.org/project/django-classy-tags/
.. |django| image:: https://img.shields.io/badge/django-1.11%20%7C%202.2%20%7C%203.0-blue.svg
    :target: https://www.djangoproject.com/
