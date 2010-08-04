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

basic_options = core.Options(
    arguments.Argument('myarg'),
)


class ClassytagsTests(unittest.TestCase):
    def test_01_simple_parsing(self):
        argparser = parser.Parser(basic_options)
        dummy_tokens = DummyTokens('myval')
        kwargs = argparser.parse(dummy_parser, dummy_tokens)
        dummy_context = DummyContext()
        self.assertEqual(kwargs['myarg'].resolve(dummy_context), 'myval')
        

suite = unittest.TestLoader().loadTestsFromTestCase(ClassytagsTests)

if __name__ == '__main__':
    unittest.main()