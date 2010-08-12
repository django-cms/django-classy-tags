from classytags import core, arguments
from django import template
from itertools import cycle as itertools_cycle
from ptesttags import pool, BaseTagObject

tpl = template.Template("{% for x in sequence %}{% cycle '1' two %}{% endfor %}")

ctx = template.Context({'sequence': range(100), 'two': 2})

lib = template.Library()

class Cycle(core.Tag):
    name = 'cycle'
    
    options = core.Options(
        arguments.MultiValueArgument('values'),
        'as',
        arguments.Argument('varname', required=False, no_resolve=True),
    )
    
    def render_tag(self, context, values, varname):
        if self not in context.render_context:
            context.render_context[self] = itertools_cycle(values)
        cycle_iter = context.render_context[self]
        value = cycle_iter.next()
        if varname:
            context[varname] = value
        return value

lib.tag(Cycle)

class CycleTag(BaseTagObject):
    template = 'tpl'
    context = 'ctx'
    library = 'lib'

pool.register('cycle', CycleTag)