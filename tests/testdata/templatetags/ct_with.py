from classytags import core, arguments
from django import template
from testdata import pool

def get_performance_suite(): # pragma: no cover
    ct_tpl = template.Template('{% ct_with "x" as x %}{{ x }}{% endwith %}')
    dj_tpl = template.Template('{% with "x" as x %}{{ x }}{% endwith %}')
    ctx = template.Context({})
    return ct_tpl, dj_tpl, ctx

register = template.Library()


class With(core.Tag):
    name = 'ct_with'
    
    options = core.Options(
        arguments.Argument('value'),
        'as',
        arguments.Argument('varname', resolve=False),
        blocks=['endwith'],
    )

    def render_tag(self, context, value, varname, endwith):
        context.push()
        context[varname] = value
        output = endwith.render(context)
        context.pop()
        return output
    
register.tag('ct_with', With)

controls = [
    ('{% with input|upper as output %}{{ output }}{% endwith %}',
     '{% ct_with input|upper as output %}{{ output }}{% endwith %}', 
     {'input': 'input'}),
]

pool.register(With, controls=controls)