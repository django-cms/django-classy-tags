# testdata import must be first for settings patching
from testdata import pool, Renderer
from classytags import arguments, core, exceptions, utils, parser, helpers
from django import template
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
import unittest


class DummyContext(dict):
    @property
    def render_context(self): # pragma: no cover
        return self


class DummyTokens(list):
    def __init__(self, *tokens):
        super(DummyTokens, self).__init__(['dummy_tag'] + list(tokens))
        
    def split_contents(self):
        return self


class DummyParser(object):
    def compile_filter(self, token):
        return utils.TemplateConstant(token)
dummy_parser = DummyParser()


class ClassytagsTests(TestCase):
    def tag_tester(self, klass, templates):
        lib = template.Library()
        lib.tag(klass)
        template.builtins.append(lib)
        self.assertTrue(klass.name in lib.tags)
        for tpl, out, ctx in templates:
            t = template.Template(tpl)
            c = template.Context(ctx)
            s = t.render(c)
            self.assertEqual(s, out)
            for key, value in ctx.items():
                self.assertEqual(c.get(key), value)            
        template.builtins.remove(lib)
    
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
        dummy_context = DummyContext()
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        dummy_tokens = DummyTokens('myval', 'myval2')
        self.assertRaises(exceptions.TooManyArguments, options.parse, dummy_parser, dummy_tokens)
        
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
        dummy_context = DummyContext()
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['optarg'].resolve(dummy_context), None)
        dummy_tokens = DummyTokens('myval', 'optval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 2)
        dummy_context = DummyContext()
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
        self.assertRaises(exceptions.ArgumentRequiredError, options.parse, dummy_parser, dummy_tokens)
        dummy_tokens = DummyTokens('myval', 'myname')
        self.assertRaises(exceptions.BreakpointExpected, options.parse, dummy_parser, dummy_tokens)
        dummy_tokens = DummyTokens('myval', 'as', 'myname', 'something')
        self.assertRaises(exceptions.BreakpointExpected, options.parse, dummy_parser, dummy_tokens)
        dummy_tokens = DummyTokens('myval', 'as', 'myname', 'using', 'something')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 3)
        dummy_context = DummyContext()
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
        dummy_context = DummyContext()
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myflag'].resolve(dummy_context), True)
        dummy_tokens = DummyTokens('off')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myflag'].resolve(dummy_context), False)
        dummy_tokens = DummyTokens('myval')
        self.assertRaises(exceptions.InvalidFlag, options.parse, dummy_parser, dummy_tokens)
        self.assertRaises(ImproperlyConfigured, arguments.Flag, 'myflag')
        # test case senstive flag
        options = core.Options(
            arguments.Flag('myflag', true_values=['on'], default=False, case_sensitive=True)
        )
        dummy_tokens = DummyTokens('On')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myflag'].resolve(dummy_context), False)
        dummy_tokens = DummyTokens('on')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myflag'].resolve(dummy_context), True)
        # test multi flag
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
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = DummyContext()
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), ['myval'])
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), ['myval', 'myval2'])
        dummy_tokens = DummyTokens('myval', 'myval2', 'myval3')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), ['myval', 'myval2', 'myval3'])
        options = core.Options(
            arguments.MultiValueArgument('myarg', max_values=2)
        )
        dummy_tokens = DummyTokens('myval')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        dummy_context = DummyContext()
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), ['myval'])
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 1)
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), ['myval', 'myval2'])
        dummy_tokens = DummyTokens('myval', 'myval2', 'myval3')
        self.assertRaises(exceptions.TooManyArguments, options.parse, dummy_parser, dummy_tokens)
        # test no resolve
        options = core.Options(
            arguments.MultiValueArgument('myarg', resolve=False)
        )
        argparser = parser.Parser(options)
        dummy_tokens = DummyTokens('myval', "'myval2'")
        kwargs, blocks = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), ['myval', 'myval2'])
        
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
        dummy_context = DummyContext()
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 4)
        for key, value in [('singlearg', 1), ('multiarg', [2,3]), ('varname', 4), ('safe', True)]:
            self.assertEqual(kwargs[key].resolve(dummy_context), value)
        # test 'only first argument given'
        dummy_tokens = DummyTokens(1)
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 4)
        for key, value in [('singlearg', 1), ('multiarg', []), ('varname', None), ('safe', False)]:
            self.assertEqual(kwargs[key].resolve(dummy_context), value)
        # test first argument and last argument given
        dummy_tokens = DummyTokens(2, 'safe', 'false')
        kwargs, blocks = options.parse(dummy_parser, dummy_tokens)
        self.assertEqual(blocks, {})
        self.assertEqual(len(kwargs), 4)
        for key, value in [('singlearg', 2), ('multiarg', []), ('varname', None), ('safe', False)]:
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
        lib = template.Library()
        lib.tag(Cycle)
        self.assertTrue('classy_cycle' in lib.tags)
        origtpl = template.Template("""
            {% for thing in sequence %}{% cycle "1" "2" "3" "4" %}{% endfor %}
        """)
        sequence = [1,2,3,4,5,6,7,8,9,10]
        context = template.Context({'sequence': sequence})
        original = origtpl.render(context)
        template.builtins.insert(0, lib)
        classytpl = template.Template("""
            {% for thing in sequence %}{% classy_cycle "1" "2" "3" "4" %}{% endfor %}
        """)
        classy = classytpl.render(context)
        self.assertEqual(original, classy)
        origtpl = template.Template("""
            {% for thing in sequence %}{% cycle "1" "2" "3" "4" as myvarname %}{% endfor %}
        """)
        sequence = [1,2,3,4,5,6,7,8,9,10]
        context = template.Context({'sequence': sequence})
        original = origtpl.render(context)
        template.builtins.insert(0, lib)
        classytpl = template.Template("""
            {% for thing in sequence %}{% classy_cycle "1" "2" "3" "4" as myvarname %}{% endfor %}
        """)
        classy = classytpl.render(context)
        self.assertEqual(original, classy)
        
    def test_08_auto_name(self):
        class MyTag(core.Tag):
            pass
        lib = template.Library()
        lib.tag(MyTag)
        self.assertTrue('my_tag' in lib.tags, "'my_tag' not in %s" % lib.tags.keys())
        
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
            ('{% hello "my friend" as othervar %}', '', {'othervar': 'hello my friend'})
        ]
        self.tag_tester(Hello, tpls)
                
    def test_10_django_vs_classy(self):
        pool.autodiscover()
        for tagname, data in pool:
            controls = data.get('controls', None)
            if not controls: # pragma: no cover
                continue
            tag = data['tag']                
            renderer = Renderer(tag)
            i = 0
            for djstring, ctstring, ctx in controls:
                i += 1
                dj = renderer.django(djstring, ctx)
                cy = renderer.classy(ctstring, ctx)
                self.assertNotEqual(djstring, ctstring)
                self.assertEqual(dj, cy,
                    ("Classytag implementation of %s (control %s) returned "
                     "something else than official tag:\n"
                     "Classy: %r\nDjango: %r" % (tagname, i, cy, dj))
                )
    
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
            ('{% blocky %}1{% a %}2{% b %}3{% c %}4{% d %}5{% e %}', '1;2;3;4;5', {},),
            ('{% blocky %}12{% b %}3{% c %}4{% d %}5{% e %}', '12;;3;4;5', {},),
            ('{% blocky %}123{% c %}4{% d %}5{% e %}', '123;;;4;5', {},),
            ('{% blocky %}1234{% d %}5{% e %}', '1234;;;;5', {},),
            ('{% blocky %}12345{% e %}', '12345;;;;', {},),
            ('{% blocky %}1{% a %}23{% c %}4{% d %}5{% e %}', '1;23;;4;5', {},),
            ('{% blocky %}1{% a %}23{% c %}45{% e %}', '1;23;;45;', {},),
        ]
        self.tag_tester(Blocky, templates)
        
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
        self.tag_tester(Dummy, templates)
        

suite = unittest.TestLoader().loadTestsFromTestCase(ClassytagsTests)

if __name__ == '__main__':
    unittest.main()