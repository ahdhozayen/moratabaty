from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def slash_split(val: str) ->str:
    return val.split('/')[0]

@register.filter
@stringfilter
def d_arrow_split(val: str) ->str:
    return val.split('>>')[0]
    