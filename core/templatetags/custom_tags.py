from django import template

register = template.Library()

## Builtin
from urllib import parse

@register.simple_tag(takes_context = True)
def url_replace(context,**kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return parse.urlencode(query)