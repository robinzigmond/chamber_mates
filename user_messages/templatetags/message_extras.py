from django import template
from django.template.defaultfilters import linebreaksbr
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
def preserve_whitespace(value):
    """
    Ensures that all linebreaks are displayed in the browser (enabled by the built-in
    linebreaksbr filter), and also that multiple spaces are not collapsed into one. I
    found how to implement the latter from StackOverflow posts and in particular
    https://djangosnippets.org/snippets/2842/
    """
    return linebreaksbr(mark_safe("&nbsp;".join(value.split(" "))))
