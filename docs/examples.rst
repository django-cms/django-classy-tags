########
Examples
########

********
Argument
********

Template tag::

    class MyTag(Tag):
        options = Options(
            Argument('firstarg'),
            Argument('secondarg', required=False, default="default"),
        )
        
        def render_tag(self, context, firstarg, secondarg):
            return 'Firstarg: %s, Secondarg: %s' % (firstarg, secondarg)


.. list-table:: Templates
   :header-rows: 1
   
   * - Template
     - Context
     - Output
   * - ``{% my_tag "firstarg" %}``
     - ``{}``
     - ``Firstarg: firstarg, Secondarg: default``
   * - ``{% my_tag firstarg %}``
     - ``{'firstarg': 'hello'}``
     - ``Firstarg: hello, Secondarg: default``
   * - ``{% my_tag "firstarg" "secondarg" %}``
     - ``{}``
     - ``Firstarg: firstarg, Secondarg: secondarg``
   * - ``{% my_tag firstarg secondarg %}``
     - ``{'firstarg': 'hello', 'secondarg': 'world'}``
     - ``Firstarg: hello, Secondarg: world``


***************
KeywordArgument
***************

Template tag::

    class MyTag(Tag):
        options = Options(
            KeywordArgument('firstarg', defaultkey='mykey', default='myvalue', required=False),
        )
        
        def render_tag(self, context, firstarg):
            return '%s: %s' % firstarg.items()[0]


.. list-table:: Templates
    :header-rows: 1
   
    * - Template
      - Context
      - Output
    * - ``{% my_tag %}``
      - ``{}``
      - ``mykey: myvalue``
    * - ``{% my_tag "value" %}``
      - ``{}``
      - ``mykey: value``
    * - ``{% my_tag key="value" %}``
      - ``{}``
      - ``key: value``
    * - ``{% my_tag value %}``
      - ``{'value': 'hello'}``
      - ``mykey: hello``
    * - ``{% my_tag key=value %}``
      - ``{'value': 'hello', 'key': 'blah'}``
      - ``key: hello``


***************
IntegerArgument
***************

Template tag::

    class MyTag(Tag):
        options = Options(
            IntegerArgument('firstarg'),
        )
        
        def render_tag(self, context, firstarg):
            return firstarg + 1


.. list-table:: Templates
    :header-rows: 1
   
    * - Template
      - Context
      - Output
    * - ``{% my_tag 4 %}``
      - ``{}``
      - ``5``
    * - ``{% my_tag "7" %}``
      - ``{}``
      - ``8``
    * - ``{% my_tag myvalue %}``
      - ``{'myvalue': 5}``
      - ``6``
    * - ``{% my_tag 'hello' %}``
      - ``{}``
      - ``1`` (with DEBUG=False)
    * - ``{% my_tag 'hello' %}``
      - ``{}``
      - raises a TemplateSyntaxError (with DEBUG=True)


**************
ChoiceArgument
**************

Template tag::

    class MyTag(Tag):
        options = Options(
            ChoiceArgument('firstarg', ['firstchoice', 'secondchoice']),
        )
        
        def render_tag(self, context, firstarg):
            return firstarg

.. list-table:: Templates
    :header-rows: 1
   
    * - Template
      - Context
      - Output
    * - ``{% my_tag 'firstchoice' %}``
      - ``{}``
      - ``firstchoice``
    * - ``{% my_tag "secondchoice" %}``
      - ``{}``
      - ``secondchoice``
    * - ``{% my_tag myvalue %}``
      - ``{'myvalue': 'firstchoice'}``
      - ``firstchoice``
    * - ``{% my_tag 'hello' %}``
      - ``{}``
      - ``'firstchoice'`` (with DEBUG=False)
    * - ``{% my_tag 'hello' %}``
      - ``{}``
      - raises a TemplateSyntaxError (with DEBUG=True)


******************
MultiValueArgument
******************

Template tag::

    class MyTag(Tag):
        options = Options(
            MultiValueArgument('firstarg', max_values=3),
        )
        
        def render_tag(self, context, firstarg):
            return ','.join(firstarg)

.. list-table:: Templates
    :header-rows: 1
   
    * - Template
      - Context
      - Output
    * - ``{% my_tag 'one' %}``
      - ``{}``
      - ``one``
    * - ``{% my_tag 'one' 'two' %}``
      - ``{}``
      - ``one,two``
    * - ``{% my_tag myvalue 'two' othervalue %}``
      - ``{'myvalue': 'eins', 'othervalue': 'drei'}``
      - ``eins,two,drei``
    * - ``{% my_tag 'one' 'two' 'three' 'four' %}``
      - ``{}``
      - raises a TooManyArguments error (subclass of TemplateSyntaxError)


********************
MultiKeywordArgument
********************

Template tag::

    class MyTag(Tag):
        options = Options(
            MultiKeywordArgument('firstarg'),
        )
        
        def render_tag(self, context, firstarg):
            output = ''
            for key, value in firstarg.items():
                output += '%s:%s, ' % (key, value)
            return output[:-2]

.. list-table:: Templates
    :header-rows: 1
   
    * - Template
      - Context
      - Output
    * - ``{% my_tag key='one' %}``
      - ``{}``
      - ``key:one,``
    * - ``{% my_tag key='one' otherkey='two' %}``
      - ``{}``
      - ``key=one, otherkey=two,``
    * - ``{% my_tag key=myvalue otherkey='two' %}``
      - ``{'myvalue': 'eins'}``
      - ``key:eins, otherkey:two,``


****
Flag
****

Template tag::

    class MyTag(Tag):
        options = Options(
            Flag('firstarg', true_values=['on', 'true', 'yes'], case_sensitive=True),
        )
        
        def render_tag(self, context, firstarg):
            if firstarg:
                return 'YES'
            else:
                return 'NO'

.. list-table:: Templates
    :header-rows: 1
   
    * - Template
      - Context
      - Output
    * - ``{% my_tag "on" %}``
      - ``{}``
      - ``YES``
    * - ``{% my_tag myvalue %}``
      - ``{'myvalue': 'yes'}``
      - ``YES``
    * - ``{% my_tag "Yes" %}``
      - ``{}``
      - ``NO``
    * - ``{% my_tag "hello world" %}``
      - ``{}``
      - ``NO``