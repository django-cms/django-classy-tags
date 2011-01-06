from classytags import core, arguments, values
from django import template
from testdata import pool
import re


def get_performance_suite(): # pragma: no cover
    ct_tpl = template.Template("{% ct_for x in sequence %}{{ forloop.counter }}: {{ x }}{% endfor %}")
    dj_tpl = template.Template("{% for x in sequence %}{{ forloop.counter }}: {{ x }}{% endfor %}")
    ctx = template.Context({'sequence': range(100)})
    return ct_tpl, dj_tpl, ctx

register = template.Library()


class CommaSeperatableSequence(values.ListValue):        
    def resolve(self, context):
        resolved = []
        base = super(CommaSeperatableSequence, self).resolve(context)
        for thing in re.sub(r' *, *', ',', ', '.join(base)).split(','):
            if thing:
                resolved.append(thing)
        return resolved


class CommaSeperatableMultiValueArgument(arguments.MultiValueArgument):
    sequence_class = CommaSeperatableSequence


class For(core.Tag):
    name = 'ct_for'
    
    options = core.Options(
        CommaSeperatableMultiValueArgument('loopvars', resolve=False),
        'in',
        arguments.Argument('values'),
        blocks=[('empty', 'pre_empty'), ('endfor', 'post_empty')],
    )
    
    def render_tag(self, context, loopvars, values, pre_empty, post_empty):
        if 'forloop' in context:
            parentloop = context['forloop']
        else:
            parentloop = {}
        context.push()
        if not hasattr(values, '__len__'):
            values = list(values)
        len_values = len(values)
        if len_values < 1:
            context.pop()
            return post_empty.render(context)
        nodelist = template.NodeList()
        unpack = len(loopvars) > 1
        # Create a forloop value in the context.  We'll update counters on each
        # iteration just below.
        loop_dict = context['forloop'] = {'parentloop': parentloop}
        for i, item in enumerate(values):
            # Shortcuts for current loop iteration number.
            loop_dict['counter0'] = i
            loop_dict['counter'] = i+1
            # Reverse counter iteration numbers.
            loop_dict['revcounter'] = len_values - i
            loop_dict['revcounter0'] = len_values - i - 1
            # Boolean values designating first and last times through loop.
            loop_dict['first'] = (i == 0)
            loop_dict['last'] = (i == len_values - 1)

            if unpack:
                # If there are multiple loop variables, unpack the item into
                # them.
                context.update(dict(zip(loopvars, item)))
            else:
                context[loopvars[0]] = item
            for node in pre_empty:
                nodelist.append(node.render(context))
            if unpack:
                # The loop variables were pushed on to the context so pop them
                # off again. This is necessary because the tag lets the length
                # of loopvars differ to the length of each set of items and we
                # don't want to leave any vars from the previous loop on the
                # context.
                context.pop()
        context.pop()
        return nodelist.render(context)
register.tag('ct_for', For)


class Iterable(object):
    def __iter__(self):
        for i in range(10):
            yield i


controls = [
    (
         "{% for x in sequence %}{{ forloop.counter }}: {{ x }},{% empty %}empty{% endfor %}",
         "{% ct_for x in sequence %}{{ forloop.counter }}: {{ x }},{% empty %}empty{% endfor %}",
         {'sequence': range(50)}
     ),
    (
         "{% for x in sequence %}{{ forloop.counter }}: {{ x }}{% empty %}empty{% endfor %}",
         "{% ct_for x in sequence %}{{ forloop.counter }}: {{ x }}{% empty %}empty{% endfor %}",
         {'sequence': range(0)}
     ),
    (
         "{% for x in sequence %}{{ forloop.counter }}: {{ x }}{% endfor %}",
         "{% ct_for x in sequence %}{{ forloop.counter }}: {{ x }}{% endfor %}",
         {'sequence': range(50)}
     ),
    (
         "{% for x in sequence %}{{ forloop.counter }}-{{ x }}:{% for y in sequence %}{{ forloop.counter }}-{{forloop.parentloop.counter }}{{ y }}{% endfor %}{% endfor %}",
         "{% ct_for x in sequence %}{{ forloop.counter }}-{{ x }}:{% ct_for y in sequence %}{{ forloop.counter }}-{{forloop.parentloop.counter }}{{ y }}{% endfor %}{% endfor %}",
         {'sequence': range(50)}
     ),
    (
         "{% for x,y in sequence %}{{ forloop.counter }}: {{ x }}-{{ y }}{% endfor %}",
         "{% ct_for x,y in sequence %}{{ forloop.counter }}: {{ x }}-{{ y }}{% endfor %}",
         {'sequence': [('a', 1), ('b', 2), ('c', 3), ('d', 4)]}
     ),
    (
         "{% for x,y in sequence %}{{ forloop.counter }}: {{ x }}-{{ y }}{% endfor %}",
         "{% ct_for x y in sequence %}{{ forloop.counter }}: {{ x }}-{{ y }}{% endfor %}",
         {'sequence': [('a', 1), ('b', 2), ('c', 3), ('d', 4)]}
     ),
    (
         "{% for x in sequence %}{{ forloop.counter }}: {{ x }}{% empty %}empty{% endfor %}",
         "{% ct_for x in sequence %}{{ forloop.counter }}: {{ x }}{% empty %}empty{% endfor %}",
         {'sequence': Iterable()}
     ),
]

pool.register(For, controls=controls)