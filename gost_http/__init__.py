"""
GOST HTTP Client - Python wrapper библиотека для работы с GOST сайтами

Эта библиотека предоставляет универсальный HTTP клиент, который автоматически
выбирает правильный метод подключения для работы с GOST сайтами:
- Использует pyOpenSSL для сайтов только с GOST cipher suites
- Использует стандартный requests для смешанных сайтов
- Fallback на subprocess с curl при необходимости
"""

import os

from .gost_http_client import (
    GOSTHTTPClient,
    gost_get,
    gost_post,
    gost_put,
    gost_delete,
    gost_patch,
    gost_head,
    gost_options,
    gost_session
)

# Импортируем requests_gost для удобного использования
from . import requests_gost

# Версия библиотеки может быть установлена через переменную окружения GOST_HTTP_VERSION
# (например, через ARG в Dockerfile для CI/CD)
__version__ = os.environ.get('GOST_HTTP_VERSION', '0.1.0')

__all__ = [
    'GOSTHTTPClient',
    'gost_get',
    'gost_post',
    'gost_put',
    'gost_delete',
    'gost_patch',
    'gost_head',
    'gost_options',
    'gost_session',
    'requests_gost'
]

