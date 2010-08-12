import os
from timeit import Timer
os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % __name__

class TagPool(dict):
    def register(self, name, tag):
        self[name] = tag()
        
    def autodiscover(self):
        for f in os.listdir(os.path.dirname(__file__)):
            if not f.endswith('.py'):
                continue
            if f.startswith('_'):
                continue
            __import__('%s.%s' % (self.__module__, f[:-3]))
        
    def __iter__(self):
        for key in sorted(self.keys()):
            yield key, self[key]

pool = TagPool()


DJANGO_SETUP = """from %s import %s, %s
from django import template
class PseudoSettings:
    TEMPLATE_DEBUG = True
    USE_I18N = False
    TEMPLATE_STRING_IF_INVALID = ''
template.settings = PseudoSettings"""


CLASSY_SETUP = """from %s import %s, %s, %s as library
from django import template
class PseudoSettings:
    TEMPLATE_DEBUG = True
    USE_I18N = False
    TEMPLATE_STRING_IF_INVALID = ''
template.settings = PseudoSettings
template.builtins.insert(0, library)"""


class BaseTagObject(object):
    template = ""
    library = ""
    context = ""
    
    def django(self, iterations):
        setup = DJANGO_SETUP % (self.__module__, self.template, self.context)
        return self._timeit(setup, iterations)
    
    def classy(self, iterations):
        setup = CLASSY_SETUP % (self.__module__, self.template, self.context, self.library)
        return self._timeit(setup, iterations)
    
    def _timeit(self, setup, iterations):
        t = Timer("tpl.render(%s)" % self.context, setup) 
        return t.timeit(iterations)