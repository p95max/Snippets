# MainApp/templatetags/lang_tags.py

from django import template

register = template.Library()

LANG_ICONS = {
    'python': 'fa-brands fa-python',
    'cpp': 'fa-solid fa-code',
    'java': 'fa-brands fa-java',
    'js': 'fa-brands fa-js',
}

@register.simple_tag
def lang_icon_class(lang):
    return LANG_ICONS.get(lang.lower(), 'fa-solid fa-file-code')
