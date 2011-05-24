from __future__ import with_statement
from classytags import (arguments, core, exceptions, utils, parser, helpers,
    values)
from classytags.blocks import BlockDefinition, VariableBlockName
from classytags.test.context_managers import SettingsOverride, TemplateTags
from django import template
from django.core.exceptions import ImproperlyConfigured
from unittest import TestCase
import sys
import warnings


class DummyTokens(list):
    def __init__(self, *tokens):
        super(DummyTokens, self).__init__(['dummy_tag'] + list(tokens))

    def split_contents(self):
        return self


class DummyParser(object):
    def compile_filter(self, token):
        return utils.TemplateConstant(token)
dummy_parser = DummyParser()


class _Warning(object):
    def __init__(self, message, category, filename, lineno):
        self.message = message
        self.category = category
        self.filename = filename
        self.lineno = lineno


def _collectWarnings(observeWarning, f, *args, **kwargs):
    def showWarning(message, category, filename, lineno, file=None, line=None):
        assert isinstance(message, Warning)
        observeWarning(_Warning(
                message.args[0], category, filename, lineno))

    # Disable the per-module cache for every module otherwise if the warning
    # which the caller is expecting us to collect was already emitted it won't
    # be re-emitted by the call to f which happens below.
    for v in sys.modules.itervalues():
        if v is not None:
            try:
                v.__warningregistry__ = None
            except:  # pragma: no cover
                # Don't specify a particular exception type to handle in case
                # some wacky object raises some wacky exception in response to
                # the setattr attempt.
                pass

    origFilters = warnings.filters[:]
    origShow = warnings.showwarning
    warnings.simplefilter('always')
    try:
        warnings.showwarning = showWarning
        result = f(*args, **kwargs)
    finally:
        warnings.filters[:] = origFilters
        warnings.showwarning = origShow
    return result


class ClassytagsTests(TestCase):
    def failUnlessWarns(self, category, message, f, *args, **kwargs):
        warningsShown = []
        result = _collectWarnings(warningsShown.append, f, *args, **kwargs)

        if not warningsShown:  # pragma: no cover
            self.fail("No warnings emitted")
        first = warningsShown[0]
        for other in warningsShown[1:]:  # pragma: no cover
            if ((other.message, other.category)
                != (first.message, first.category)):
                self.fail("Can't handle different warnings")
        self.assertEqual(first.message, message)
        self.assertTrue(first.category is category)

        return result
    assertWarns = failUnlessWarns

    def _tag_tester(self, klass, templates):
        """
        Helper method to test a template tag by rendering it and checkout
        output.

        *klass* is a template tag class (subclass of core.Tag)
        *templates* is a sequence of a triple (template-string, output-string,
        context)
        """

        TAG_MESSAGE = ("Rendering of template %(in)r resulted in "
                       "%(realout)r, expected %(out)r using %(ctx)r.")

        with TemplateTags(klass):
            for tpl, out, ctx in templates:
                t = template.Template(tpl)
                c = template.Context(ctx)
                s = t.render(c)
                self.assertEqual(s, out, TAG_MESSAGE % {
                    'in': tpl,
                    'out': out,
                    'ctx': ctx,
                    'realout': s,
                })
                for key, value in ctx.items():
                    self.assertEqual(c.get(key), value)

    def test_01_simple_parsing(self):
        """
        Test very basic single argument parsing
        """
        options = core.Options(
            arguments.Argument('myarg'),
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        dummy_tokens = DummyTokens('myval', 'myval2')
        self.assertRaises(exceptions.TooManyArguments,
                          options.parse, dummy_parser, dummy_tokens)

    def test_02_optional(self):
        """
        Test basic optional argument parsing
        """
        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('optarg', required=False, default=None),
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['optarg'].resolve(dummy_context), None)
        dummy_tokens = DummyTokens('myval', 'optval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['optarg'].resolve(dummy_context), 'optval')

    def test_03_breakpoints(self):
        """
        Test parsing with breakpoints
        """
        options = core.Options(
            arguments.Argument('myarg'),
            'as',
            arguments.Argument('varname'),
            'using',
            arguments.Argument('using'),
        )
        dummy_tokens = DummyTokens('myval')
        self.assertRaises(exceptions.ArgumentRequiredError,
                          options.parse, dummy_parser, dummy_tokens)
        dummy_tokens = DummyTokens('myval', 'myname')
        self.assertRaises(exceptions.BreakpointExpected,
                          options.parse, dummy_parser, dummy_tokens)
        dummy_tokens = DummyTokens('myval', 'as', 'myname', 'something')
        self.assertRaises(exceptions.BreakpointExpected,
                          options.parse, dummy_parser, dummy_tokens)
        dummy_tokens = DummyTokens('myval', 'as', 'myname', 'using',
                                   'something')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 3)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['varname'].resolve(dummy_context), 'myname')
        self.assertEqual(kwargs['using'].resolve(dummy_context), 'something')

    def test_04_flag(self):
        """
        Test flag arguments
        """
        options = core.Options(
            arguments.Flag('myflag', true_values=['on'], false_values=['off'])
        )
        dummy_tokens = DummyTokens('on')
        dummy_context = {}
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myflag'].resolve(dummy_context), True)
        dummy_tokens = DummyTokens('off')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myflag'].resolve(dummy_context), False)
        # test exceptions
        dummy_tokens = DummyTokens('myval')
        self.assertRaises(exceptions.InvalidFlag,
                          options.parse, dummy_parser, dummy_tokens)
        options = core.Options(
            arguments.Flag('myflag', true_values=['on'])
        )
        dummy_tokens = DummyTokens('myval')
        self.assertRaises(exceptions.InvalidFlag,
                          options.parse, dummy_parser, dummy_tokens)
        options = core.Options(
            arguments.Flag('myflag', false_values=['off'])
        )
        dummy_tokens = DummyTokens('myval')
        self.assertRaises(exceptions.InvalidFlag,
                          options.parse, dummy_parser, dummy_tokens)
        self.assertRaises(ImproperlyConfigured, arguments.Flag, 'myflag')
        # test case sensitive flag
        options = core.Options(
            arguments.Flag('myflag', true_values=['on'], default=False,
                           case_sensitive=True)
        )
        dummy_tokens = DummyTokens('On')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myflag'].resolve(dummy_context), False)
        dummy_tokens = DummyTokens('on')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myflag'].resolve(dummy_context), True)
        # test multi-flag
        options = core.Options(
            arguments.Flag('flagone', true_values=['on'], default=False),
            arguments.Flag('flagtwo', false_values=['off'], default=True),
        )
        dummy_tokens = DummyTokens('On', 'On')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['flagone'].resolve(dummy_context), True)
        self.assertEqual(kwargs['flagtwo'].resolve(dummy_context), True)

    def test_05_multi_value(self):
        """
        Test simple multi value arguments
        """
        options = core.Options(
            arguments.MultiValueArgument('myarg')
        )
        # test single token MVA
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        # test resolving to list
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), ['myval'])
        # test double token MVA
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        self.assertEqual(kwargs['myarg'].resolve(dummy_context),
                         ['myval', 'myval2'])
        # test triple token MVA
        dummy_tokens = DummyTokens('myval', 'myval2', 'myval3')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        self.assertEqual(kwargs['myarg'].resolve(dummy_context),
                         ['myval', 'myval2', 'myval3'])
        # test max_values option
        options = core.Options(
            arguments.MultiValueArgument('myarg', max_values=2)
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), ['myval'])
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        self.assertEqual(kwargs['myarg'].resolve(dummy_context),
                         ['myval', 'myval2'])
        dummy_tokens = DummyTokens('myval', 'myval2', 'myval3')
        self.assertRaises(exceptions.TooManyArguments,
                          options.parse, dummy_parser, dummy_tokens)
        # test no resolve
        options = core.Options(
            arguments.MultiValueArgument('myarg', resolve=False)
        )
        argparser = parser.Parser(options)
        dummy_tokens = DummyTokens('myval', "'myval2'")
        kwargs, blocks = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myarg'].resolve(dummy_context),
                         ['myval', 'myval2'])
        # test default
        options = core.Options(
            arguments.MultiValueArgument('myarg', default=['hello', 'world']),
        )
        argparser = parser.Parser(options)
        dummy_tokens = DummyTokens()
        kwargs, blocks = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myarg'].resolve(dummy_context),
                         ['hello', 'world'])

    def test_06_complex(self):
        """
        test a complex tag option parser
        """
        options = core.Options(
            arguments.Argument('singlearg'),
            arguments.MultiValueArgument('multiarg', required=False),
            'as',
            arguments.Argument('varname', required=False),
            'safe',
            arguments.Flag('safe', true_values=['on', 'true'], default=False)
        )
        # test simple 'all arguments given'
        dummy_tokens = DummyTokens(1, 2, 3, 'as', 4, 'safe', 'true')
        dummy_context = {}
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 4)
        expected = [
            ('singlearg', 1),
            ('multiarg', [2, 3]),
            ('varname', 4),
            ('safe', True)
        ]
        for key, value in expected:
            self.assertEqual(kwargs[key].resolve(dummy_context), value)
        # test 'only first argument given'
        dummy_tokens = DummyTokens(1)
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 4)
        expected = [
            ('singlearg', 1),
            ('multiarg', []),
            ('varname', None),
            ('safe', False)
        ]
        for key, value in expected:
            self.assertEqual(kwargs[key].resolve(dummy_context), value)
        # test first argument and last argument given
        dummy_tokens = DummyTokens(2, 'safe', 'false')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 4)
        expected = [
            ('singlearg', 2),
            ('multiarg', []),
            ('varname', None),
            ('safe', False)
        ]
        for key, value in expected:
            self.assertEqual(kwargs[key].resolve(dummy_context), value)

    def test_07_cycle(self):
        """
        This test re-implements django's cycle tag (because it's quite crazy)
        and checks if it works.
        """
        from itertools import cycle as itertools_cycle

        class Cycle(core.Tag):
            name = 'classy_cycle'

            options = core.Options(
                arguments.MultiValueArgument('values'),
                'as',
                arguments.Argument('varname', required=False, resolve=False),
            )

            def render_tag(self, context, values, varname):
                if self not in context.render_context:
                    context.render_context[self] = itertools_cycle(values)
                cycle_iter = context.render_context[self]
                value = cycle_iter.next()
                if varname:
                    context[varname] = value
                return value

        origtpl = template.Template(
            '{% for thing in sequence %}'
            '{% cycle "1" "2" "3" "4" %}'
            '{% endfor %}'
        )
        sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        context = template.Context({'sequence': sequence})
        original = origtpl.render(context)
        with TemplateTags(Cycle):
            classytpl = template.Template(
                '{% for thing in sequence %}'
                '{% classy_cycle "1" "2" "3" "4" %}'
                '{% endfor %}'
            )
            classy = classytpl.render(context)
        self.assertEqual(original, classy)
        origtpl = template.Template(
            '{% for thing in sequence %}'
            '{% cycle "1" "2" "3" "4" as myvarname %}'
            '{% endfor %}'
        )
        sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        context = template.Context({'sequence': sequence})
        original = origtpl.render(context)
        with TemplateTags(Cycle):
            classytpl = template.Template(
                '{% for thing in sequence %}'
                '{% classy_cycle "1" "2" "3" "4" as myvarname %}'
                '{% endfor %}'
            )
            classy = classytpl.render(context)
        self.assertEqual(original, classy)

    def test_08_naming(self):
        # test implicit naming
        class MyTag(core.Tag):
            pass
        lib = template.Library()
        lib.tag(MyTag)
        msg = "'my_tag' not in %s" % lib.tags.keys()
        self.assertTrue('my_tag' in lib.tags, msg)
        # test explicit naming

        class MyTag2(core.Tag):
            name = 'my_tag_2'

        lib = template.Library()
        lib.tag(MyTag2)
        msg = "'my_tag_2' not in %s" % lib.tags.keys()
        self.assertTrue('my_tag_2' in lib.tags, msg)
        # test named registering
        lib = template.Library()
        lib.tag('my_tag_3', MyTag)
        msg = "'my_tag_3' not in %s" % lib.tags.keys()
        self.assertTrue('my_tag_3' in lib.tags, msg)
        msg = "'my_tag' in %s" % lib.tags.keys()
        self.assertTrue('my_tag' not in lib.tags, msg)
        lib = template.Library()
        lib.tag('my_tag_4', MyTag2)
        msg = "'my_tag_4' not in %s" % lib.tags.keys()
        self.assertTrue('my_tag_4' in lib.tags, msg)
        msg = "'my_tag2' in %s" % lib.tags.keys()
        self.assertTrue('my_tag2' not in lib.tags, msg)

    def test_09_hello_world(self):
        class Hello(core.Tag):
            options = core.Options(
                arguments.Argument('name', required=False, default='world'),
                'as',
                arguments.Argument('varname', required=False, resolve=False)
            )

            def render_tag(self, context, name, varname):
                output = 'hello %s' % name
                if varname:
                    context[varname] = output
                    return ''
                return output
        tpls = [
            ('{% hello %}', 'hello world', {}),
            ('{% hello "classytags" %}', 'hello classytags', {}),
            ('{% hello as myvar %}', '', {'myvar': 'hello world'}),
            ('{% hello "my friend" as othervar %}', '',
             {'othervar': 'hello my friend'})
        ]
        self._tag_tester(Hello, tpls)

    def test_11_blocks(self):
        class Blocky(core.Tag):
            options = core.Options(
                blocks=['a', 'b', 'c', 'd', 'e'],
            )

            def render_tag(self, context, **nodelists):
                tpl = "%(a)s;%(b)s;%(c)s;%(d)s;%(e)s"
                data = {}
                for key, value in nodelists.items():
                    data[key] = value.render(context)
                return tpl % data
        templates = [
            ('{% blocky %}1{% a %}2{% b %}3{% c %}4{% d %}5{% e %}',
             '1;2;3;4;5', {},),
            ('{% blocky %}12{% b %}3{% c %}4{% d %}5{% e %}', '12;;3;4;5',
             {},),
            ('{% blocky %}123{% c %}4{% d %}5{% e %}', '123;;;4;5', {},),
            ('{% blocky %}1234{% d %}5{% e %}', '1234;;;;5', {},),
            ('{% blocky %}12345{% e %}', '12345;;;;', {},),
            ('{% blocky %}1{% a %}23{% c %}4{% d %}5{% e %}', '1;23;;4;5',
             {},),
            ('{% blocky %}1{% a %}23{% c %}45{% e %}', '1;23;;45;', {},),
        ]
        self._tag_tester(Blocky, templates)

    def test_12_astag(self):
        class Dummy(helpers.AsTag):
            options = core.Options(
                'as',
                arguments.Argument('varname', resolve=False, required=False),
            )

            def get_value(self, context):
                return "dummy"
        templates = [
            ('{% dummy %}:{{ varname }}', 'dummy:', {},),
            ('{% dummy as varname %}:{{ varname }}', ':dummy', {},),
        ]
        self._tag_tester(Dummy, templates)

    def test_13_inclusion_tag(self):
        class Inc(helpers.InclusionTag):
            template = 'test.html'

            options = core.Options(
                arguments.Argument('var'),
            )

            def get_context(self, context, var):
                return {'var': var}
        templates = [
            ('{% inc var %}', 'inc', {'var': 'inc'},),
        ]
        self._tag_tester(Inc, templates)

        class Inc2(helpers.InclusionTag):
            template = 'test.html'

        templates = [
            ('{% inc2 %}', '', {},),
        ]
        self._tag_tester(Inc2, templates)

    def test_14_integer_variable(self):
        options = core.Options(
            arguments.IntegerArgument('integer', resolve=False),
        )
        # test okay
        with SettingsOverride(DEBUG=False):
            dummy_tokens = DummyTokens('1')
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            dummy_context = {}
            self.assertEqual(kwargs['integer'].resolve(dummy_context), 1)
            # test warning
            dummy_tokens = DummyTokens('one')
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            dummy_context = {}
            one = repr('one')
            message = arguments.IntegerValue.errors['clean'] % {'value': one}
            self.assertWarns(exceptions.TemplateSyntaxWarning,
                             message, kwargs['integer'].resolve, dummy_context)
            self.assertEqual(kwargs['integer'].resolve(dummy_context),
                             values.IntegerValue.value_on_error)
            # test exception
        with SettingsOverride(DEBUG=True):
            dummy_tokens = DummyTokens('one')
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            dummy_context = {}
            message = values.IntegerValue.errors['clean'] % {
                'value': repr('one')
            }
            self.assertRaises(template.TemplateSyntaxError,
                              kwargs['integer'].resolve, dummy_context)
        # test the same as above but with resolving

        class IntegerTag(core.Tag):
            options = core.Options(
                arguments.IntegerArgument('integer')
            )

            def render_tag(self, context, integer):
                return integer

        with TemplateTags(IntegerTag):
            tpl = template.Template("{% integer_tag i %}")
        with SettingsOverride(DEBUG=False):
            # test okay
            context = template.Context({'i': '1'})
            self.assertEqual(tpl.render(context), '1')
            # test warning
            context = template.Context({'i': 'one'})
            message = values.IntegerValue.errors['clean'] % {
                 'value': repr('one')
            }
            self.assertWarns(exceptions.TemplateSyntaxWarning,
                             message, tpl.render, context)
            self.assertEqual(int(tpl.render(context)),
                             values.IntegerValue.value_on_error)
        # test exception
        with SettingsOverride(DEBUG=True):
            context = template.Context({'i': 'one'})
            message = arguments.IntegerValue.errors['clean'] % {'value': one}
            self.assertRaises(template.TemplateSyntaxError, tpl.render,
                              context)
            # reset settings

    def test_15_not_implemented_errors(self):
        class Fail(core.Tag):
            pass

        class Fail2(helpers.AsTag):
            pass

        class Fail3(helpers.AsTag):
            options = core.Options(
                'as',
            )

        class Fail4(helpers.AsTag):
            options = core.Options(
                'as',
                arguments.Argument('varname', resolve=False),
            )

        class Fail5(helpers.InclusionTag):
            pass

        with TemplateTags(Fail, Fail2, Fail3, Fail4, Fail5):
            context = template.Context({})
            tpl = template.Template("{% fail %}")
            self.assertRaises(NotImplementedError, tpl.render, context)
            self.assertRaises(ImproperlyConfigured,
                              template.Template, "{% fail2 %}")
            self.assertRaises(ImproperlyConfigured,
                              template.Template, "{% fail3 %}")
            tpl = template.Template("{% fail4 as something %}")
            self.assertRaises(NotImplementedError, tpl.render, context)
            self.assertRaises(ImproperlyConfigured,
                              template.Template, "{% fail5 %}")

    def test_16_too_many_arguments(self):
        class NoArg(core.Tag):
            pass
        with TemplateTags(NoArg):
            self.assertRaises(exceptions.TooManyArguments,
                              template.Template, "{% no_arg a arg %}")

    def test_17_choice_argument(self):
        options = core.Options(
            arguments.ChoiceArgument('choice',
                                     choices=['one', 'two', 'three']),
        )
        # this is settings dependant!
        with SettingsOverride(DEBUG=True):
            for good in ('one', 'two', 'three'):
                dummy_tokens = DummyTokens(good)
                kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
                dummy_context = {}
                self.assertEqual(kwargs['choice'].resolve(dummy_context), good)
            bad = 'four'
            dummy_tokens = DummyTokens(bad)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            dummy_context = {}
            self.assertRaises(template.TemplateSyntaxError,
                              kwargs['choice'].resolve, dummy_context)
        with SettingsOverride(DEBUG=False):
            self.assertEqual(kwargs['choice'].resolve(dummy_context), 'one')
            # test other value class

            class IntegerChoiceArgument(arguments.ChoiceArgument):
                value_class = values.IntegerValue

            default = 2
            options = core.Options(
                IntegerChoiceArgument('choice', choices=[1, 2, 3],
                                      default=default),
            )
        with SettingsOverride(DEBUG=True):
            for good in ('1', '2', '3'):
                dummy_tokens = DummyTokens(good)
                kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
                dummy_context = {}
                self.assertEqual(kwargs['choice'].resolve(dummy_context),
                                 int(good))
            bad = '4'
            dummy_tokens = DummyTokens(bad)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            dummy_context = {}
            self.assertRaises(template.TemplateSyntaxError,
                              kwargs['choice'].resolve, dummy_context)
        with SettingsOverride(DEBUG=False):
            self.assertEqual(kwargs['choice'].resolve(dummy_context), default)
            # reset settings

    def test_18_keyword_argument(self):
        class KeywordArgumentTag(core.Tag):
            name = 'kwarg_tag'
            options = core.Options(
                arguments.KeywordArgument('named', defaultkey='defaultkey'),
            )

            def render_tag(self, context, named):
                return '%s:%s' % (named.keys()[0], named.values()[0])

        ctx = {'key': 'thekey', 'value': 'thevalue'}
        templates = [
            ("{% kwarg_tag key='value' %}", 'key:value', ctx),
            ("{% kwarg_tag 'value' %}", 'defaultkey:value', ctx),
            ("{% kwarg_tag key=value %}", 'key:thevalue', ctx),
            ("{% kwarg_tag value %}", 'defaultkey:thevalue', ctx),
        ]
        self._tag_tester(KeywordArgumentTag, templates)

        class KeywordArgumentTag2(KeywordArgumentTag):
            name = 'kwarg_tag'
            options = core.Options(
                arguments.KeywordArgument(
                    'named',
                    defaultkey='defaultkey',
                    resolve=False,
                    required=False,
                    default='defaultvalue'
                ),
            )

        templates = [
            ("{% kwarg_tag %}", 'defaultkey:defaultvalue', ctx),
            ("{% kwarg_tag key='value' %}", 'key:value', ctx),
            ("{% kwarg_tag 'value' %}", 'defaultkey:value', ctx),
            ("{% kwarg_tag key=value %}", 'key:value', ctx),
            ("{% kwarg_tag value %}", 'defaultkey:value', ctx),
        ]
        self._tag_tester(KeywordArgumentTag2, templates)

    def test_19_multi_keyword_argument(self):
        opts = core.Options(
            arguments.MultiKeywordArgument('multi', max_values=2),
        )

        class MultiKeywordArgumentTag(core.Tag):
            name = 'multi_kwarg_tag'
            options = opts

            def render_tag(self, context, multi):
                items = sorted(multi.items())
                return ','.join(['%s:%s' % item for item in items])

        ctx = {'key': 'thekey', 'value': 'thevalue'}
        templates = [
            ("{% multi_kwarg_tag key='value' key2='value2' %}",
             'key:value,key2:value2', ctx),
            ("{% multi_kwarg_tag key=value %}", 'key:thevalue', ctx),
        ]
        self._tag_tester(MultiKeywordArgumentTag, templates)
        dummy_tokens = DummyTokens('key="value"', 'key2="value2"',
                                   'key3="value3"')
        self.assertRaises(exceptions.TooManyArguments,
                          opts.parse, dummy_parser, dummy_tokens)

    def test_20_custom_parser(self):
        class CustomParser(parser.Parser):
            def parse_blocks(self):
                return

        options = core.Options(
            blocks=[
                ('end_my_tag', 'nodelist'),
            ],
            parser_class=CustomParser
        )
        dummy_tokens = DummyTokens()
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})

    def test_21_repr(self):
        class MyTag(core.Tag):
            name = 'mytag'
        tag = MyTag(dummy_parser, DummyTokens())
        self.assertEqual('<Tag: mytag>', repr(tag))

    def test_22_non_required_multikwarg(self):
        options = core.Options(
            arguments.MultiKeywordArgument('multi', required=False),
        )
        dummy_tokens = DummyTokens()
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertTrue('multi' in kwargs)
        self.assertEqual(kwargs['multi'], {})
        options = core.Options(
            arguments.MultiKeywordArgument('multi', required=False,
                                           default={'hello': 'world'}),
        )
        dummy_tokens = DummyTokens()
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertTrue('multi' in kwargs)
        self.assertEqual(kwargs['multi'].resolve({}), {'hello': 'world'})

    def test_23_resolve_kwarg(self):
        class ResolveKwarg(core.Tag):
            name = 'kwarg'
            options = core.Options(
                arguments.KeywordArgument('named'),
            )

            def render_tag(self, context, named):
                return '%s:%s' % (named.keys()[0], named.values()[0])

        class NoResolveKwarg(core.Tag):
            name = 'kwarg'
            options = core.Options(
                arguments.KeywordArgument('named', resolve=False),
            )

            def render_tag(self, context, named):
                return '%s:%s' % (named.keys()[0], named.values()[0])

        resolve_templates = [
            ("{% kwarg key=value %}", "key:test", {'value': 'test'}),
            ("{% kwarg key='value' %}", "key:value", {'value': 'test'}),
        ]

        noresolve_templates = [
            ("{% kwarg key=value %}", "key:value", {'value': 'test'}),
        ]

        self._tag_tester(ResolveKwarg, resolve_templates)
        self._tag_tester(NoResolveKwarg, noresolve_templates)

    def test_24_kwarg_default(self):
        options = core.Options(
            arguments.KeywordArgument('kwarg', required=False,
                                      defaultkey='mykey'),
        )
        dummy_tokens = DummyTokens()
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertTrue('kwarg' in kwargs)
        self.assertEqual(kwargs['kwarg'].resolve({}), {'mykey': None})
        options = core.Options(
            arguments.KeywordArgument('kwarg', required=False,
                                      default='hello'),
        )
        dummy_tokens = DummyTokens()
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertTrue('kwarg' in kwargs)
        self.assertEqual(kwargs['kwarg'].resolve({}), {})
        options = core.Options(
            arguments.KeywordArgument('kwarg', required=False,
                                      default='hello', defaultkey='key'),
        )
        dummy_tokens = DummyTokens()
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertTrue('kwarg' in kwargs)
        self.assertEqual(kwargs['kwarg'].resolve({}), {'key': 'hello'})

    def test_25_multikwarg_no_key(self):
        options = core.Options(
            arguments.MultiKeywordArgument('multi'),
        )
        with SettingsOverride(DEBUG=True):
            dummy_tokens = DummyTokens('value')
            self.assertRaises(template.TemplateSyntaxError,
                              options.parse, dummy_parser, dummy_tokens)
        with SettingsOverride(DEBUG=False):
            dummy_tokens = DummyTokens('value')
            self.assertRaises(template.TemplateSyntaxError,
                              options.parse, dummy_parser, dummy_tokens)

    def test_26_inclusion_tag_context_pollution(self):
        """
        Check the `keep_render_context` and `push_pop_context` attributes on
        InclusionTag work as advertised and prevent 'context pollution'
        """
        class NoPushPop(helpers.InclusionTag):
            template = 'inclusion.html'

            def get_context(self, context):
                return context.update({'pollution': True})

        class Standard(helpers.InclusionTag):
            template = 'inclusion.html'

            def get_context(self, context):
                return {'pollution': True}

        with TemplateTags(NoPushPop, Standard):
            # push pop pollution
            ctx1 = template.Context({'pollution': False})
            tpl1 = template.Template("{% no_push_pop %}")
            tpl1.render(ctx1)
            self.assertEqual(ctx1['pollution'], True)
            ctx2 = template.Context({'pollution': False})
            tpl2 = template.Template("{% standard %}")
            tpl2.render(ctx2)
            self.assertEqual(ctx2['pollution'], False)

    def test_27_named_block(self):
        class StartBlock(core.Tag):
            options = core.Options(
                arguments.Argument("myarg"),
                blocks=[
                    BlockDefinition("nodelist",
                                    VariableBlockName("end_block %(value)s",
                                                      'myarg'),
                                    "end_block")
                ]
            )

            def render_tag(self, context, myarg, nodelist):
                return "nodelist:%s;myarg:%s" % (nodelist.render(context),
                                                 myarg)

        with TemplateTags(StartBlock):
            ctx = template.Context()
            tpl = template.Template(
                "{% start_block 'hello' %}nodelist-content"
                "{% end_block 'hello' %}"
            )
            output = tpl.render(ctx)
            expected_output = 'nodelist:nodelist-content;myarg:hello'
            self.assertEqual(output, expected_output)

            ctx = template.Context({'hello': 'world'})
            tpl = template.Template(
                "{% start_block hello %}nodelist-content{% end_block hello %}"
            )
            output = tpl.render(ctx)
            expected_output = 'nodelist:nodelist-content;myarg:world'
            self.assertEqual(output, expected_output)

    def test_28_fail_named_block(self):
        vbn = VariableBlockName('endblock %(value)s', 'myarg')
        self.assertRaises(ImproperlyConfigured, core.Options,
                          blocks=[BlockDefinition('nodelist', vbn)])

    def test_29_named_block_noresolve(self):
        class StartBlock(core.Tag):
            options = core.Options(
                arguments.Argument("myarg", resolve=False),
                blocks=[
                    BlockDefinition("nodelist",
                                    VariableBlockName("end_block %(value)s",
                                                      'myarg'),
                                    "end_block")
                ]
            )

            def render_tag(self, context, myarg, nodelist):
                return "nodelist:%s;myarg:%s" % (nodelist.render(context),
                                                 myarg)

        with TemplateTags(StartBlock):
            ctx = template.Context()
            tpl = template.Template(
                "{% start_block 'hello' %}nodelist-content"
                "{% end_block 'hello' %}"
            )
            output = tpl.render(ctx)
            expected_output = 'nodelist:nodelist-content;myarg:hello'
            self.assertEqual(output, expected_output)
