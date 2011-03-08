##################
Arguments in depth
##################

Examples given here are in tabular form. The non-standard options are a list of
options to the argument class which are not the default value. The input is the
single token in your template tag that gets consumed by this argument class. The
output is the value you get in your ``render_tag`` method for the keyword of
this argument. 


Context for all examples: ``{'name': 'classytags'}``

********
Argument
********

.. list-table:: Examples
   :header-rows: 1
   
   * - Non-standard options
     - Input
     - Output
   * - 
     - ``name``
     - ``'classytags'``
   * - 
     - ``'name'``
     - ``'name'``
   * - ``resolve=False``
     - ``name``
     - ``'name'``
   * - ``default='myvalue'``
     - 
     - ``'myvalue'``


***************
KeywordArgument
***************

.. list-table:: Examples
   :header-rows: 1
   
   * - Non-standard options
     - Input
     - Output
   * - 
     - ``key=name``
     - ``{'key': 'classytags'}``
   * - 
     - ``key='name'``
     - ``{'key': 'name'}``
   * - ``defaultkey='mykey'``
     - ``name``
     - ``{'defaultkey': 'classytags'}``
   * - ``defaultkey='mykey'``
     - 
     - ``{'mykey': None}``
   * - ``resolve=False``
     - ``key=name``
     - ``{'key': 'name'}``
   * - ``splitter='->'``
     - ``key=name->'value'``
     - ``{'key=name': 'value'}``

***************
IntegerArgument
***************

.. list-table:: Examples
   :header-rows: 1
   
   * - Non-standard options
     - Input
     - Output
   * - 
     - ``'1'``
     - ``1``
   * - 
     - ``name``
     - ``0``


**************
ChoiceArgument
**************

.. list-table:: Examples
   :header-rows: 1
   
   * - Non-standard options
     - Input
     - Output
   * - ``choices=['choice']``
     - ``name``
     - ``'choice'``
   * - ``choices=['choice', 'classytags']``
     - ``name``
     - ``'classytags'``


******************
MultiValueArgument
******************

.. list-table:: Examples
   :header-rows: 1
   
   * - Non-standard options
     - Input
     - Output
   * - 
     - 
     - ``[]``
   * - 
     - ``name 'is' 'awesome'``
     - ``['classytags', 'is', 'awesome']``


********************
MultiKeywordArgument
********************

.. list-table:: Examples
   :header-rows: 1
   
   * - Non-standard options
     - Input
     - Output
   * - 
     - 
     - ``{}``
   * - 
     - ``name=name awesome='yes'``
     - ``{'name': 'classytags', 'awesome': 'yes'}``
   * - ``splitter=':', resolve=False``
     - ``hello:world``
     - ``{'hello': 'world'}``


****
Flag
****

.. list-table:: Examples
   :header-rows: 1
   
   * - Non-standard options
     - Input
     - Output
   * - ``true_values=['true', 'yes']``
     - ``name``
     - ``False``
   * - ``true_values=['true', 'yes']``
     - ``'YES'``
     - ``True``
   * - ``true_values=['true', 'yes'], case_sensitive=True``
     - ``'YES'``
     - ``False``