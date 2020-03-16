####### extra template tags ##########

from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter(name="highlight")
def highlight(text, word):
    return format_html(text.replace(word, "<span class='highlight'>%s</span>" % word))

@register.filter(name='format')
def format(value, fmt):
    return fmt.format(value)