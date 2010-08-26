from classytags import core, arguments, values
from django import template
from itertools import cycle as itertools_cycle
from testdata import pool


def get_performance_suite():# pragma: no cover
    ct_tpl = template.Template("{% for x in sequence %}{% ct_cycle '1' two %}{% endfor %}")
    dj_tpl = template.Template("{% for x in sequence %}{% cycle '1' two %}{% endfor %}")
    ctx = template.Context({'sequence': range(100), 'two': 2})
    return ct_tpl, dj_tpl, ctx

register = template.Library()


class LazyListValue(values.ListValue):
    def resolve(self, context):
        return self


class LazyMVA(arguments.MultiValueArgument):
    sequence_class = LazyListValue


class Cycle(core.Tag):
    name = 'ct_cycle'
    
    options = core.Options(
        LazyMVA('values'),
        'as',
        arguments.Argument('varname', required=False, resolve=False),
    )
    
    def render_tag(self, context, values, varname):
        if self not in context.render_context:
            context.render_context[self] = itertools_cycle(values)
        cycle_iter = context.render_context[self]
        value = cycle_iter.next().resolve(context)
        if varname:
            context[varname] = value
        return value
register.tag('ct_cycle', Cycle)

controls = [
    (
         "{% for x in sequence %}{% cycle '1' two %}{% endfor %}",
         "{% for x in sequence %}{% ct_cycle '1' two %}{% endfor %}",
         {'two': 2, 'sequence': range(50)}
     ),
    (
         "{% for x in sequence %}{% cycle '1' two as varname %}{{ varname }}{% endfor %}",
         "{% for x in sequence %}{% ct_cycle '1' two as varname %}{{ varname }}{% endfor %}",
         {'two': 2, 'sequence': range(50)}
    ),
]

pool.register(Cycle, controls=controls)