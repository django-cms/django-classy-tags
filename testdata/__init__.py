from django import template
from timeit import Timer
import os
os.environ['DJANGO_SETTINGS_MODULE'] = '%s._settings' % __name__

class TagPool(dict):
    def register(self, tag, **data):
        data.update({'tag': tag})
        self[tag.name] = data
        
    def autodiscover(self):
        for f in os.listdir(os.path.join(os.path.dirname(__file__), 'templatetags/')):
            if not f.endswith('.py'):
                continue
            __import__('%s.templatetags.%s' % (self.__module__, f[:-3]))
        
    def __iter__(self):
        for key in sorted(self.keys()):
            yield key, self[key]

pool = TagPool()


DJANGO_SETUP = """from %s import get_performance_suite, register
from django import template
class PseudoSettings:
    TEMPLATE_DEBUG = True
    USE_I18N = False
    TEMPLATE_STRING_IF_INVALID = ''
template.settings = PseudoSettings
template.builtins.insert(0, register)
ct_tpl, dj_tpl, ctx = get_performance_suite()
tpl = dj_tpl"""


CLASSY_SETUP = """from %s import get_performance_suite, register
from django import template
class PseudoSettings:
    TEMPLATE_DEBUG = True
    USE_I18N = False
    TEMPLATE_STRING_IF_INVALID = ''
template.settings = PseudoSettings
template.builtins.insert(0, register)
ct_tpl, dj_tpl, ctx = get_performance_suite()
tpl = ct_tpl"""


class Benchmark(object): # pragma: no cover
    def __init__(self, tag):
        self.mod = tag.__module__
        
    def django(self, iterations):
        setup = DJANGO_SETUP % self.mod
        return self._timeit(setup, iterations)
    
    def classy(self, iterations):
        setup = CLASSY_SETUP % self.mod
        return self._timeit(setup, iterations)
    
    def _timeit(self, setup, iterations):
        t = Timer("tpl.render(ctx)", setup) 
        return t.timeit(iterations)


class Renderer(object):
    def __init__(self, tag):
        self.tag = tag
        self.libname = self.tag.__module__.split('.')[-1]
        
    def django(self, tplstring, data):
        tpl = template.Template(tplstring)
        ctx = template.Context(data)
        return tpl.render(ctx)
    
    def classify(self, tplstring):
        return "{%% load %s %%}%s" % (self.libname, tplstring)
    
    def classy(self, tplstring, data):
        rendered = self.django(self.classify(tplstring), data)
        return rendered