from classytags import arguments, core, exceptions, utils, parser
import unittest


class DummyContext(dict):
    @property
    def render_context(self):
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


class ClassytagsTests(unittest.TestCase):
    def test_01_simple_parsing(self):
        """
        Test very basic single argument parsing
        """
        options = core.Options(
            arguments.Argument('myarg'),
        )
        argparser = parser.Parser(options)
        dummy_tokens = DummyTokens('myval')
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(len(kwargs), 1)
        dummy_context = DummyContext()
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        dummy_tokens = DummyTokens('myval', 'myval2')
        self.assertRaises(exceptions.TooManyArguments, argparser.parse, dummy_parser, dummy_tokens)
        
    def test_02_optional(self):
        """
        Test basic optional argument parsing
        """
        options = core.Options(
            arguments.Argument('myarg'),
            arguments.Argument('optarg', required=False, default=None),
        )
        argparser = parser.Parser(options)
        dummy_tokens = DummyTokens('myval')
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(len(kwargs), 2)
        dummy_context = DummyContext()
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['optarg'].resolve(dummy_context), None)
        dummy_tokens = DummyTokens('myval', 'optval')
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
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
        )
        argparser = parser.Parser(options)
        dummy_tokens = DummyTokens('myval')
        self.assertRaises(exceptions.ArgumentRequiredError, argparser.parse, dummy_parser, dummy_tokens)
        dummy_tokens = DummyTokens('myval', 'myname')
        self.assertRaises(exceptions.BreakpointExpected, argparser.parse, dummy_parser, dummy_tokens)
        dummy_tokens = DummyTokens('myval', 'as', 'myname')
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(len(kwargs), 2)
        dummy_context = DummyContext()
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        self.assertEqual(kwargs['varname'].resolve(dummy_context), 'myname')
        
    def test_04_flag(self):
        options = core.Options(
            arguments.Flag('myflag', true_values=['on'], false_values=['off'])
        )
        argparser = parser.Parser(options)
        dummy_tokens = DummyTokens('on')
        dummy_context = DummyContext()
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(kwargs['myflag'].resolve(dummy_context), True)
        dummy_tokens = DummyTokens('off')
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(kwargs['myflag'].resolve(dummy_context), False)
        dummy_tokens = DummyTokens('myval')
        self.assertRaises(exceptions.InvalidFlag, argparser.parse, dummy_parser, dummy_tokens)
        
    def test_05_multi_value(self):
        options = core.Options(
            arguments.MultiValueArgument('myarg')
        )
        argparser = parser.Parser(options)
        dummy_tokens = DummyTokens('myval')
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(len(kwargs), 1)
        dummy_context = DummyContext()
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), ['myval'])
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(len(kwargs), 1)
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), ['myval', 'myval2'])
        dummy_tokens = DummyTokens('myval', 'myval2', 'myval3')
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(len(kwargs), 1)
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), ['myval', 'myval2', 'myval3'])
        options = core.Options(
            arguments.MultiValueArgument('myarg', max_values=2)
        )
        argparser = parser.Parser(options)
        dummy_tokens = DummyTokens('myval')
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(len(kwargs), 1)
        dummy_context = DummyContext()
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), ['myval'])
        dummy_tokens = DummyTokens('myval', 'myval2')
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(len(kwargs), 1)
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), ['myval', 'myval2'])
        dummy_tokens = DummyTokens('myval', 'myval2', 'myval3')
        self.assertRaises(exceptions.TooManyArguments, argparser.parse, dummy_parser, dummy_tokens)
        
    def test_06_complex(self):
        options = core.Options(
            arguments.Argument('singlearg'),
            arguments.MultiValueArgument('multiarg', required=False),
            'as',
            arguments.Argument('varname', required=False),
            'safe',
            arguments.Flag('safe', true_values=['on', 'true'], default=False)
        )
        argparser = parser.Parser(options)
        dummy_tokens = DummyTokens(1, 2, 3, 'as', 4, 'safe', 'true')
        dummy_context = DummyContext()
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(len(kwargs), 4)
        for key, value in [('singlearg', 1), ('multiarg', [2,3]), ('varname', 4), ('safe', True)]:
            self.assertEqual(kwargs[key].resolve(dummy_context), value)
        dummy_tokens = DummyTokens(1)
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
        self.assertEqual(len(kwargs), 4)
        for key, value in [('singlearg', 1), ('multiarg', []), ('varname', None), ('safe', False)]:
            self.assertEqual(kwargs[key].resolve(dummy_context), value)


suite = unittest.TestLoader().loadTestsFromTestCase(ClassytagsTests)

if __name__ == '__main__':
    unittest.main()