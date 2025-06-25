"""
Патч для обеспечения совместимости pymorphy2 с Python 3.11

Проблема в том, что pymorphy2 использует устаревшую функцию inspect.getargspec(),
которая была удалена в Python 3.11.
"""
import inspect
import sys
from collections import namedtuple

# Определяем ArgSpec, если его нет
if not hasattr(inspect, 'ArgSpec'):
    inspect.ArgSpec = namedtuple('ArgSpec', ['args', 'varargs', 'keywords', 'defaults'])

# Добавляем getargspec для совместимости с Python 3.11+
def _getargspec_backport(func):
    """
    Эмуляция inspect.getargspec() через современный inspect.getfullargspec()
    """
    full_spec = inspect.getfullargspec(func)
    return inspect.ArgSpec(
        args=full_spec.args,
        varargs=full_spec.varargs,
        keywords=full_spec.varkw,
        defaults=full_spec.defaults,
    )

# Добавляем getargspec в модуль inspect, если её нет
if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = _getargspec_backport
