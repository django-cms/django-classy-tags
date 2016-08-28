from __future__ import with_statement

import os
import sys
import warnings
from distutils.version import LooseVersion
import operator
from unittest import TestCase

import django
from django import template
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, RequestContext
from django.test import RequestFactory

from classytags import arguments
from classytags import core
from classytags import exceptions
from classytags import helpers
from classytags import parser
from classytags import utils
from classytags import values
from classytags.blocks import BlockDefinition
from classytags.blocks import VariableBlockName
from classytags.compat import compat_next
from classytags.test.context_managers import SettingsOverride
from classytags.test.context_managers import TemplateTags

DJANGO_1_4_OR_HIGHER = (
    LooseVersion(django.get_version()) >= LooseVersion('1.4')
)
DJANGO_1_5_OR_HIGHER = (
    LooseVersion(django.get_version()) >= LooseVersion('1.5')
)

CLASSY_TAGS_DIR = os.path.abspath(os.path.dirname(__file__))


class DummyTokens(list):
    def __init__(self, *tokens):
        super(DummyTokens, self).__init__(['dummy_tag'] + list(tokens))

    def split_contents(self):
        return self


class DummyParser(object):
    @staticmethod
    def compile_filter(token):
        return utils.TemplateConstant(token)
dummy_parser = DummyParser()


class _Warning(object):
    def __init__(self, message, category, filename, lineno):
        self.message = message
        self.category = category
        self.filename = filename
        self.lineno = lineno


def _collect_warnings(observe_warning, f, *args, **kwargs):
    def show_warning(message, category, filename, lineno, file=None,
                     line=None):
        assert isinstance(message, Warning)
        observe_warning(
            _Warning(message.args[0], category, filename, lineno)
        )

    # Disable the per-module cache for every module otherwise if the warning
    # which the caller is expecting us to collect was already emitted it won't
    # be re-emitted by the call to f which happens below.
    for v in sys.modules.values():  # pragma: no cover
        if v is not None:
            try:
                v.__warningregistry__ = None
            except:
                # Don't specify a particular exception type to handle in case
                # some wacky object raises some wacky exception in response to
                # the setattr attempt.
                pass

    orig_filters = warnings.filters[:]
    orig_show = warnings.showwarning
    warnings.simplefilter('always')
    try:
        warnings.showwarning = show_warning
        result = f(*args, **kwargs)
    finally:
        warnings.filters[:] = orig_filters
        warnings.showwarning = orig_show
    return result


class ClassytagsTests(TestCase):
    def failUnlessWarns(self, category, message, f, *args, **kwargs):
        warnings_shown = []
        result = _collect_warnings(warnings_shown.append, f, *args, **kwargs)

        if not warnings_shown:  # pragma: no cover
            self.fail("No warnings emitted")
        first = warnings_shown[0]
        for other in warnings_shown[1:]:  # pragma: no cover
            if ((other.message, other.category) !=
                    (first.message, first.category)):
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

        tag_message = ("Rendering of template %(in)r resulted in "
                       "%(realout)r, expected %(out)r using %(ctx)r.")

        with TemplateTags(klass):
            for tpl, out, ctx in templates:
                t = template.Template(tpl)
                c = template.Context(ctx)
                s = t.render(c)
                self.assertEqual(s, out, tag_message % {
                    'in': tpl,
                    'out': out,
                    'ctx': ctx,
                    'realout': s,
                })
                for key, value in ctx.items():
                    self.assertEqual(c.get(key), value)

    def test_simple_parsing(self):
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

    def test_simple_parsing_too_many_arguments(self):
        options = core.Options(
            arguments.Argument('myarg'),
        )
        dummy_tokens = DummyTokens('myval', 'myval2')
        self.assertRaises(exceptions.TooManyArguments,
                          options.parse, dummy_parser, dummy_tokens)

    def test_optional_default(self):
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

    def test_optional_given(self):
        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('optarg', required=False, default=None),
        )
        dummy_tokens = DummyTokens('myval', 'optval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['optarg'].resolve(dummy_context), 'optval')

    def test_breakpoints_not_enough_arguments(self):
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

    def test_breakpoint_breakpoint_expected(self):
        options = core.Options(
            arguments.Argument('myarg'),
            'as',
            arguments.Argument('varname'),
            'using',
            arguments.Argument('using'),
        )
        dummy_tokens = DummyTokens('myval', 'myname')
        self.assertRaises(exceptions.BreakpointExpected,
                          options.parse, dummy_parser, dummy_tokens)

    def test_breakpoint_breakpoint_expected_second(self):
        options = core.Options(
            arguments.Argument('myarg'),
            'as',
            arguments.Argument('varname'),
            'using',
            arguments.Argument('using'),
        )
        dummy_tokens = DummyTokens('myval', 'as', 'myname', 'something')
        self.assertRaises(exceptions.BreakpointExpected,
                          options.parse, dummy_parser, dummy_tokens)

    def test_breakpoint_trailing(self):
        options = core.Options(
            arguments.Argument('myarg'),
            'as',
            arguments.Argument('varname', required=False),
        )
        dummy_tokens = DummyTokens('myval', 'as')
        self.assertRaises(exceptions.TrailingBreakpoint,
                          options.parse, dummy_parser, dummy_tokens)

    def test_breakpoint_okay(self):
        options = core.Options(
            arguments.Argument('myarg'),
            'as',
            arguments.Argument('varname'),
            'using',
            arguments.Argument('using'),
        )
        dummy_tokens = DummyTokens('myval', 'as', 'myname', 'using',
                                   'something')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 3)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['varname'].resolve(dummy_context), 'myname')
        self.assertEqual(kwargs['using'].resolve(dummy_context), 'something')

    def test_flag_true_value(self):
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

    def test_flag_false_value(self):
        options = core.Options(
            arguments.Flag('myflag', true_values=['on'], false_values=['off'])
        )
        dummy_tokens = DummyTokens('off')
        dummy_context = {}
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myflag'].resolve(dummy_context), False)

    def test_flag_wrong_value(self):
        options = core.Options(
            arguments.Flag('myflag', true_values=['on'], false_values=['off'])
        )
        # test exceptions
        dummy_tokens = DummyTokens('myval')
        self.assertRaises(exceptions.InvalidFlag,
                          options.parse, dummy_parser, dummy_tokens)

    def test_flag_wrong_value_no_false(self):
        options = core.Options(
            arguments.Flag('myflag', true_values=['on'])
        )
        dummy_tokens = DummyTokens('myval')
        self.assertRaises(exceptions.InvalidFlag,
                          options.parse, dummy_parser, dummy_tokens)

    def test_flag_wrong_value_no_true(self):
        options = core.Options(
            arguments.Flag('myflag', false_values=['off'])
        )
        dummy_tokens = DummyTokens('myval')
        self.assertRaises(exceptions.InvalidFlag,
                          options.parse, dummy_parser, dummy_tokens)
        self.assertRaises(ImproperlyConfigured, arguments.Flag, 'myflag')

    def test_case_sensitive_flag_typo(self):
        # test case sensitive flag
        options = core.Options(
            arguments.Flag('myflag', true_values=['on'], default=False,
                           case_sensitive=True)
        )
        dummy_tokens = DummyTokens('On')
        dummy_context = {}
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myflag'].resolve(dummy_context), False)

    def test_case_sensitive_flag_okay(self):
        options = core.Options(
            arguments.Flag(
                'myflag',
                true_values=['on'],
                default=False,
                case_sensitive=True
            )
        )
        dummy_tokens = DummyTokens('on')
        dummy_context = {}
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myflag'].resolve(dummy_context), True)

    def test_multiflag(self):
        # test multi-flag
        options = core.Options(
            arguments.Flag('flagone', true_values=['on'], default=False),
            arguments.Flag('flagtwo', false_values=['off'], default=True),
        )
        dummy_tokens = DummyTokens('On', 'On')
        dummy_context = {}
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['flagone'].resolve(dummy_context), True)
        self.assertEqual(kwargs['flagtwo'].resolve(dummy_context), True)

    def test_multi_value_single_value(self):
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

    def test_multi_value_two_values(self):
        options = core.Options(
            arguments.MultiValueArgument('myarg')
        )
        # test double token MVA
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context),
                         ['myval', 'myval2'])

    def test_multi_value_three_values(self):
        options = core.Options(
            arguments.MultiValueArgument('myarg')
        )
        # test triple token MVA
        dummy_tokens = DummyTokens('myval', 'myval2', 'myval3')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context),
                         ['myval', 'myval2', 'myval3'])

    def test_multi_value_max_values_single(self):
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

    def test_multi_value_max_values_double(self):
        options = core.Options(
            arguments.MultiValueArgument('myarg', max_values=2)
        )
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context),
                         ['myval', 'myval2'])

    def test_multi_value_max_values_too_many(self):
        options = core.Options(
            arguments.MultiValueArgument('myarg', max_values=2)
        )
        dummy_tokens = DummyTokens('myval', 'myval2', 'myval3')
        self.assertRaises(exceptions.TooManyArguments,
                          options.parse, dummy_parser, dummy_tokens)

    def test_multi_value_no_resolve(self):
        # test no resolve
        options = core.Options(
            arguments.MultiValueArgument('myarg', resolve=False)
        )
        argparser = parser.Parser(options)
        dummy_tokens = DummyTokens('myval', "'myval2'")
        kwargs, blocks = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context),
                         ['myval', 'myval2'])

    def test_multi_value_defaults(self):
        # test default
        options = core.Options(
            arguments.MultiValueArgument('myarg', default=['hello', 'world']),
        )
        argparser = parser.Parser(options)
        dummy_tokens = DummyTokens()
        kwargs, blocks = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        dummy_context = {}
        self.assertEqual(kwargs['myarg'].resolve(dummy_context),
                         ['hello', 'world'])

    def test_complex_all_arguments(self):
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

    def test_complex_only_first_argument(self):
        options = core.Options(
            arguments.Argument('singlearg'),
            arguments.MultiValueArgument('multiarg', required=False),
            'as',
            arguments.Argument('varname', required=False),
            'safe',
            arguments.Flag('safe', true_values=['on', 'true'], default=False)
        )
        # test 'only first argument given'
        dummy_tokens = DummyTokens(1)
        dummy_context = {}
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

    def test_complext_first_and_last_argument(self):
        options = core.Options(
            arguments.Argument('singlearg'),
            arguments.MultiValueArgument('multiarg', required=False),
            'as',
            arguments.Argument('varname', required=False),
            'safe',
            arguments.Flag('safe', true_values=['on', 'true'], default=False)
        )
        # test first argument and last argument given
        dummy_tokens = DummyTokens(2, 'safe', 'false')
        dummy_context = {}
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

    def test_cycle(self):
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
                value = compat_next(cycle_iter)
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

    def test_naming(self):
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

    def test_hello_world(self):
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

    def test_filters_in_arguments(self):
        class Filtered(core.Tag):
            options = core.Options(
                arguments.Argument('value'),
            )

            def render_tag(self, context, value):
                return value
        tpls = [
            ('{% filtered "hello" %}', 'hello', {}),
            ('{% filtered var %}', 'world', {'var': 'world'}),
            ('{% filtered var|default:"foo" %}', 'foo', {}),
        ]
        self._tag_tester(Filtered, tpls)

    def test_filtered_multi_keyword(self):
        class Filtered(core.Tag):
            options = core.Options(
                arguments.MultiKeywordArgument('kwargs'),
            )

            def render_tag(self, context, kwargs):
                return '|'.join('%s:%s' % (k, v) for k, v in kwargs.items())
        tpls = [
            ('{% filtered hello="world" %}', 'hello:world', {}),
            ('{% filtered hello=var %}', 'hello:world', {'var': 'world'}),
            ('{% filtered hello=var|default:"foo" %}', 'hello:foo', {}),
        ]
        self._tag_tester(Filtered, tpls)

    def test_blocks(self):
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

    def test_astag(self):
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

    def test_inclusion_tag(self):
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

    def test_inclusion_tag_push_pop_context(self):
        class IncPollute(helpers.InclusionTag):
            template = 'test.html'

            options = core.Options(
                arguments.Argument('var')
            )

            def get_context(self, context, var):
                context.update({'var': 'polluted'})
                return context

        with TemplateTags(IncPollute):
            tpl = template.Template('{% inc_pollute var %}')
            ctx = template.Context({'var': 'test'})
            out = tpl.render(ctx)
            self.assertEqual(out, 'polluted')
            self.assertEqual(ctx['var'], 'polluted')

        # now enable pollution control
        IncPollute.push_context = True

        with TemplateTags(IncPollute):
            tpl = template.Template('{% inc_pollute var %}')
            ctx = template.Context({'var': 'test'})
            out = tpl.render(ctx)
            self.assertEqual(out, 'polluted')
            self.assertEqual(ctx['var'], 'test')

    def test_integer_variable(self):
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

    def test_not_implemented_errors(self):
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

        if DJANGO_1_4_OR_HIGHER:
            exc_class = NotImplementedError
        else:  # pragma: no cover
            exc_class = template.TemplateSyntaxError

        with TemplateTags(Fail, Fail2, Fail3, Fail4):
            context = template.Context({})
            tpl = template.Template("{% fail %}")
            self.assertRaises(exc_class, tpl.render, context)
            self.assertRaises(ImproperlyConfigured,
                              template.Template, "{% fail2 %}")
            self.assertRaises(ImproperlyConfigured,
                              template.Template, "{% fail3 %}")
            tpl = template.Template("{% fail4 as something %}")
            self.assertRaises(exc_class, tpl.render, context)

    def test_too_many_arguments(self):
        class NoArg(core.Tag):
            pass
        with TemplateTags(NoArg):
            self.assertRaises(exceptions.TooManyArguments,
                              template.Template, "{% no_arg a arg %}")

    def test_choice_argument(self):
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

    def test_keyword_argument(self):
        class KeywordArgumentTag(core.Tag):
            name = 'kwarg_tag'
            options = core.Options(
                arguments.KeywordArgument('named', defaultkey='defaultkey'),
            )

            def render_tag(self, context, named):
                return '%s:%s' % (
                    list(named.keys())[0], list(named.values())[0]
                )

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

    def test_multi_keyword_argument(self):
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

    def test_custom_parser(self):
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

    def test_repr(self):
        class MyTag(core.Tag):
            name = 'mytag'
        tag = MyTag(dummy_parser, DummyTokens())
        self.assertEqual('<Tag: mytag>', repr(tag))

    def test_non_required_multikwarg(self):
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

    def test_resolve_kwarg(self):
        class ResolveKwarg(core.Tag):
            name = 'kwarg'
            options = core.Options(
                arguments.KeywordArgument('named'),
            )

            def render_tag(self, context, named):
                return '%s:%s' % (
                    list(named.keys())[0], list(named.values())[0]
                )

        class NoResolveKwarg(core.Tag):
            name = 'kwarg'
            options = core.Options(
                arguments.KeywordArgument('named', resolve=False),
            )

            def render_tag(self, context, named):
                return '%s:%s' % (
                    list(named.keys())[0], list(named.values())[0]
                )

        resolve_templates = [
            ("{% kwarg key=value %}", "key:test", {'value': 'test'}),
            ("{% kwarg key='value' %}", "key:value", {'value': 'test'}),
        ]

        noresolve_templates = [
            ("{% kwarg key=value %}", "key:value", {'value': 'test'}),
        ]

        self._tag_tester(ResolveKwarg, resolve_templates)
        self._tag_tester(NoResolveKwarg, noresolve_templates)

    def test_kwarg_default(self):
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

    def test_multikwarg_no_key(self):
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

    def test_inclusion_tag_context_pollution(self):
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

    def test_named_block(self):
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

    def test_fail_named_block(self):
        vbn = VariableBlockName('endblock %(value)s', 'myarg')
        self.assertRaises(ImproperlyConfigured, core.Options,
                          blocks=[BlockDefinition('nodelist', vbn)])

    def test_named_block_noresolve(self):
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

    def test_strict_string(self):
        options = core.Options(
            arguments.StringArgument('string', resolve=False),
        )
        with SettingsOverride(DEBUG=False):
            # test ok
            dummy_tokens = DummyTokens('string')
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            dummy_context = {}
            self.assertEqual(
                kwargs['string'].resolve(dummy_context), 'string'
            )
            # test warning
            dummy_tokens = DummyTokens(1)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            dummy_context = {}
            message = values.StrictStringValue.errors['clean'] % {
                'value': repr(1)
            }
            self.assertWarns(
                exceptions.TemplateSyntaxWarning,
                message,
                kwargs['string'].resolve,
                dummy_context
            )
        with SettingsOverride(DEBUG=True):
            # test exception
            dummy_tokens = DummyTokens(1)
            kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
            dummy_context = {}
            self.assertRaises(
                template.TemplateSyntaxError,
                kwargs['string'].resolve,
                dummy_context
            )

    def test_get_value_for_context(self):
        message = 'exception handled'

        class MyException(Exception):
            pass

        class SuppressException(helpers.AsTag):
            options = core.Options(
                arguments.Argument('name'),
                'as',
                arguments.Argument('var', resolve=False, required=False),
            )

            def get_value(self, context, name):
                raise MyException(name)

            def get_value_for_context(self, context, name):
                try:
                    return self.get_value(context, name)
                except MyException:
                    return message

        dummy_tokens_with_as = DummyTokens('name', 'as', 'var')
        tag = SuppressException(DummyParser(), dummy_tokens_with_as)
        context = {}
        self.assertEqual(tag.render(context), '')
        self.assertEqual(context['var'], message)

        dummy_tokens_no_as = DummyTokens('name')
        tag = SuppressException(DummyParser(), dummy_tokens_no_as)
        self.assertRaises(MyException, tag.render, {})


class MultiBreakpointTests(TestCase):
    def test_optional_firstonly(self):
        options = core.Options(
            arguments.Argument('first'),
            'also',
            'using',
            arguments.Argument('second', required=False),
        )
        # check only using the first argument
        dummy_tokens = DummyTokens('firstval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['first'].resolve(dummy_context), 'firstval')
        self.assertEqual(kwargs['second'].resolve(dummy_context), None)

    def test_optional_both(self):
        options = core.Options(
            arguments.Argument('first'),
            'also',
            'using',
            arguments.Argument('second', required=False),
        )
        # check using both arguments and both breakpoints
        dummy_tokens = DummyTokens('firstval', 'also', 'using', 'secondval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = {}
        self.assertEqual(kwargs['first'].resolve(dummy_context), 'firstval')
        self.assertEqual(kwargs['second'].resolve(dummy_context), 'secondval')

    def test_partial_breakpoints(self):
        options = core.Options(
            arguments.Argument('first'),
            'also',
            'using',
            arguments.Argument('second', required=False),
        )
        # check only using the first breakpoint
        dummy_tokens = DummyTokens('firstval', 'also')
        self.assertRaises(
            exceptions.TrailingBreakpoint,
            options.parse, dummy_parser, dummy_tokens
        )

    def test_partial_breakpoints_second(self):
        options = core.Options(
            arguments.Argument('first'),
            'also',
            'using',
            arguments.Argument('second', required=False),
        )
        # check only using the second breakpoint
        dummy_tokens = DummyTokens('firstval', 'using')
        self.assertRaises(
            exceptions.BreakpointExpected,
            options.parse, dummy_parser, dummy_tokens
        )

    def test_partial_breakpoints_both(self):
        options = core.Options(
            arguments.Argument('first'),
            'also',
            'using',
            arguments.Argument('second', required=False),
        )
        # check only using the first breakpoint
        dummy_tokens = DummyTokens('firstval', 'also', 'secondval')
        # should raise an exception
        self.assertRaises(
            exceptions.BreakpointExpected,
            options.parse, dummy_parser, dummy_tokens
        )

    def test_partial_breakpoints_second_both(self):
        options = core.Options(
            arguments.Argument('first'),
            'also',
            'using',
            arguments.Argument('second', required=False),
        )
        # check only using the second breakpoint
        dummy_tokens = DummyTokens('firstval', 'using', 'secondval')
        self.assertRaises(
            exceptions.BreakpointExpected,
            options.parse, dummy_parser, dummy_tokens
        )

    def test_partial_breakpoints_both_trailing(self):
        options = core.Options(
            arguments.Argument('first'),
            'also',
            'using',
            arguments.Argument('second', required=False),
        )
        dummy_tokens = DummyTokens('firstval', 'also', 'using')
        self.assertRaises(
            exceptions.TrailingBreakpoint,
            options.parse, dummy_parser, dummy_tokens
        )

    def test_add_options(self):
        options1 = core.Options(
            arguments.Argument('first')
        )
        options2 = core.Options(
            arguments.Argument('second')
        )
        combined = options1 + options2
        self.assertEqual(len(combined.options), 1, combined.options)
        self.assertIn(None, combined.options)
        self.assertEqual(len(combined.options[None]), 2, combined.options[None])
        self.assertEqual(combined.all_argument_names, ['first', 'second'])
        self.assertEqual(len(combined.blocks), 0, combined.blocks)

    def test_add_options_blocks_first(self):
        options1 = core.Options(
            arguments.Argument('first'),
            blocks=['a']
        )
        options2 = core.Options(
            arguments.Argument('second'),
        )
        combined = options1 + options2
        self.assertEqual(len(combined.blocks), 1, combined.blocks)
        self.assertEqual(combined.blocks[0].alias, 'a')
        self.assertEqual(combined.blocks[0].names, ('a', ))

    def test_add_options_blocks_second(self):
        options1 = core.Options(
            arguments.Argument('first'),
        )
        options2 = core.Options(
            arguments.Argument('second'),
            blocks=['a']
        )
        combined = options1 + options2
        self.assertEqual(len(combined.blocks), 1, combined.blocks)
        self.assertEqual(combined.blocks[0].alias, 'a')
        self.assertEqual(combined.blocks[0].names, ('a', ))

    def test_add_options_blocks_both(self):
        options1 = core.Options(
            arguments.Argument('first'),
            blocks=['a'],
        )
        options2 = core.Options(
            arguments.Argument('second'),
            blocks=['a']
        )
        self.assertRaises(
            ValueError,
            operator.add,
            options1,
            options2,
        )

    def test_add_options_not_options(self):
        options = core.Options(
            arguments.Argument('first'),
        )
        self.assertRaises(
            TypeError,
            operator.add,
            options,
            1
        )

    def test_add_options_custom_parser_same(self):
        class CustomParser(parser.Parser):
            def parse_blocks(self):
                return

        options1 = core.Options(
            parser_class=CustomParser,
        )
        options2 = core.Options(
            parser_class=CustomParser,
        )
        combined = options1 + options2
        self.assertIs(combined.parser_class, CustomParser)

    def test_add_options_custom_parser_different(self):
        class CustomParser(parser.Parser):
            def parse_blocks(self):
                return

        options1 = core.Options(
            parser_class=CustomParser,
        )
        options2 = core.Options(
            parser_class=parser.Parser,
        )
        self.assertRaises(
            ValueError,
            operator.add,
            options1,
            options2,
        )

    def test_repr(self):
        options = core.Options(
            arguments.Argument('first'),
            'breakpoint',
            arguments.Flag('flag', true_values=['yes']),
            blocks=['block']
        )
        self.assertEqual(
            repr(options),
            '<Options:<Argument: first>,breakpoint,<Flag: flag>;block>'
        )

    def test_flatten_context(self):
        context = Context({'foo': 'bar'})
        context.push()
        context.update({'bar': 'baz'})
        context.push()
        context.update({'foo': 'test'})
        flat = utils.flatten_context(context)
        expected = {
            'foo': 'test',
            'bar': 'baz',
        }
        if DJANGO_1_5_OR_HIGHER:
            expected.update({
                'None': None,
                'True': True,
                'False': False,
            })
        self.assertEqual(flat, expected)
        context.flatten = None
        flat = utils.flatten_context(context)
        self.assertEqual(flat, expected)
        flat = utils.flatten_context({'foo': 'test', 'bar': 'baz'})
        self.assertEqual(flat, {'foo': 'test', 'bar': 'baz'})

    def test_flatten_requestcontext(self):
        factory = RequestFactory()
        request = factory.get('/')
        expected = {
            'foo': 'test',
            'request': 'bar',
            'bar': 'baz',
        }
        if DJANGO_1_5_OR_HIGHER:
            expected.update({
                'None': None,
                'True': True,
                'False': False,
            })

        checked_keys = expected.keys()

        # Adding a requestcontext to a plain context
        context = Context({'foo': 'bar'})
        context.push()
        context.update({'bar': 'baz'})
        context.push()
        rcontext = RequestContext(request, {})
        rcontext.update({'request': 'bar'})
        context.update(rcontext)
        context.push()
        context.update({'foo': 'test'})
        flat = utils.flatten_context(context)
        self.assertEqual(
            expected, dict(filter(lambda item: item[0] in checked_keys, flat.items()))
        )

        # Adding a plain context to a requestcontext
        context = RequestContext(request, {})
        context.update({'request': 'bar'})
        normal_context = Context({'foo': 'bar'})
        context.push()
        context.update({'bar': 'baz'})
        context.push()
        context.update(normal_context)
        context.push()
        context.update({'foo': 'test'})
        flat = utils.flatten_context(context)
        self.assertEqual(
            expected, dict(filter(lambda item: item[0] in checked_keys, flat.items()))
        )

        # Adding a requestcontext to a requestcontext
        context = RequestContext(request, {})
        context.update({'request': 'bar'})
        rcontext = RequestContext(request, {'foo': 'bar'})
        context.push()
        context.update({'bar': 'baz'})
        context.push()
        context.update(rcontext)
        context.push()
        context.update({'foo': 'test'})
        flat = utils.flatten_context(context)
        self.assertEqual(
            expected, dict(filter(lambda item: item[0] in checked_keys, flat.items()))
        )
