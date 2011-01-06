from classytags import core, arguments
from django import template
from django.utils.encoding import smart_unicode
from testdata import pool


def get_performance_suite(): # pragma: no cover
    ct_tpl = template.Template('{% ct_firstof a b c d %}')
    dj_tpl = template.Template('{% firstof a b c d %}')
    ctx = template.Context({'b': 'b'})
    return ct_tpl, dj_tpl, ctx

register = template.Library()


class Firstof(core.Tag):
    name = 'ct_firstof'
    
    options = core.Options(
        arguments.MultiValueArgument('values'),
    )

    def render_tag(self, context, values):
        for value in values:
            if value:
                return smart_unicode(value)
        return u''
    
register.tag('ct_firstof', Firstof)

controls = [
    ('{% firstof a b c d %}', '{% ct_firstof a b c d %}', {'b':'b'}),
    ('{% firstof a b c d %}', '{% ct_firstof a b c d %}', {}),
]

pool.register(Firstof, controls=controls)