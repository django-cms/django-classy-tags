#########
Changelog
#########

*****
0.5.3
*****

* Adopt changes to the Django 1.8 test module. Breaks backward compatibility to Django 1.2 for the tests.


*****
0.5.2
*****

* Added :attr:`classytags.helpers.InclusionTag.push_context`.


*****
0.5.1
*****

* Fixed :attr:`classytags.helpers.InclusionTag.template` being required.



*****
0.5.0
*****

* Added Python 3 support
* Added :ref:`advanced-block-definition`.
* Added :doc:`arguments` documentation.

*****
0.3.3
*****

* Fixed issues with :class:`classytags.helpers.InclusionTag``.

*****
0.3.2
*****

* Fixed issue in :class:`classytags.arguments.MultiKeywordArgument` and
  :class:`classytags.arguments.KeywordArgument` and their behavior when given
  a default value.
  
*****
0.3.1
*****

* Fixed :class:`classytags.arguments.MultiKeywordArgument` and
  :class:`classytags.arguments.KeywordArgument` not returning sane defaults.
* Added ``child_nodelist`` attribute on tag instances as well as setting the
  child nodelists as attributes onto the instance during initialization for
  compatiblity with applications that require these attributes to be set.

*****
0.3.0
*****

* Added :class:`classytags.arguments.KeywordArgument`
* Added :class:`classytags.arguments.MultiKeywordArgument`
* Added :class:`classytags.arguments.ChoiceArgument` 
* Added ability to override the parser class in the initialization of the
  :class:`classytags.core.Options` class, to make the usage of custom parsers
  easier.
* Added :class:`classytags.values.DictValue`
* Added :class:`classytags.values.ChoiceValue`

*****
0.2.2
*****

* Fixed issue in :class:`classytags.helpers.AsTag` when trying to extract the
  variable to store the value in, but no argument is given.
* Fixed :class:`classytags.helpers.InclusionTag` not validating the ``template``
  attribute on initialization.
  
*****
0.2.1
*****

* Fixed version in documentation not matching release version.

*****
0.2.0
*****

* Added ability to have typed arguments.
* Added :class:`classytags.arguments.IntegerArgument`
* Added more graceful failing in non-debug mode by using warnings instead of
  exceptions.
  
*****
0.1.3
*****

* Added :class:`classytags.helpers.InclusionTag`
