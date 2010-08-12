from classytags import core, arguments
from django import template
from ptesttags import pool, BaseTagObject

tpl = template.Template('{% now "jS o\f F" %}')

ctx = template.Context({})

lib = template.Library()


class Now(core.Tag):
    name = 'now'
    
    options = core.Options(
        arguments.Argument('format_string'),
    )

    def render_tag(self, context, format_string):
        from datetime import datetime
        from django.utils.dateformat import DateFormat
        df = DateFormat(datetime.now())
        return df.format(format_string)
    
lib.tag(Now)

class CycleTag(BaseTagObject):
    template = 'tpl'
    context = 'ctx'
    library = 'lib'

pool.register('now', CycleTag)