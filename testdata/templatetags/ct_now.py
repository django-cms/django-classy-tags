from classytags import core, arguments
from django import template
from testdata import pool


def get_performance_suite(): # pragma: no cover
    ct_tpl = template.Template('{% ct_now "jS o\f F" %}')
    dj_tpl = template.Template('{% now "jS o\f F" %}')
    ctx = template.Context({})
    return ct_tpl, dj_tpl, ctx

register = template.Library()


class Now(core.Tag):
    name = 'ct_now'
    
    options = core.Options(
        arguments.Argument('format_string'),
    )

    def render_tag(self, context, format_string):
        from datetime import datetime
        from django.utils.dateformat import DateFormat
        df = DateFormat(datetime.now())
        return df.format(format_string)
    
register.tag('ct_now', Now)

controls = [
    ('{% now "jS o\f F" %}', '{% ct_now "jS o\f F" %}', {}),
]

pool.register(Now, controls=controls)