# recipes/templatetags/recipe_extras.py

from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter
def highlight(text, query):
    """Подсвечивает найденные слова в тексте"""
    if not query or not text:
        return text

    # Разбиваем запрос на слова
    words = re.split(r'[,\s]+', query)
    for word in words:
        if len(word) < 2:
            continue
        # Ищем слово без учета регистра и подсвечиваем
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        text = pattern.sub(lambda m: f'<span class="highlight">{m.group()}</span>', str(text))

    return mark_safe(text)