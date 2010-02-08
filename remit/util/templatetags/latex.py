#!/usr/bin/python
# Inspired by and partially copied from ESP's backslash stuff

from django import template
register = template.Library()

@register.filter
def texescape(value):
    value = unicode(value).strip()
    special_backslash = '!!!12345623456!!!'
    value = value.replace('\\', special_backslash)
    for char in '&$%#_{}':
        value = value.replace(char, '\\' + char)
    value = value.replace('^', '\\textasciicircum')
    value = value.replace('~', '$\sim$')
    value = value.replace(special_backslash, '$\\backslash$')
    return value
