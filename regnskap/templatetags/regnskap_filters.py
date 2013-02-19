from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def no_break(value):
    return value.replace(u" ",u"\u00A0").replace(u"-",u"\u2011")