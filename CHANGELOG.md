# Changelog

Все значимые изменения в этом проекте будут документироваться в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и этот проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

## [0.1.1] - 2025-12-12

### Added
- Поддержка POST запросов с form data (`application/x-www-form-urlencoded`)
- Поддержка POST запросов с JSON данными
- Автоматический fallback на curl для POST/PUT/PATCH запросов при ошибках SSL
- Функция `_post_via_curl()` для отправки POST запросов через curl
- Метод `_post_via_curl()` в классе `GOSTHTTPClient`
- Пример использования POST запросов в `examples/gost_requests_post.py`

### Changed
- Метод `_request()` теперь использует curl fallback для POST/PUT/PATCH запросов аналогично GET запросам
- Обновлена документация в README.md с примерами POST запросов

### Fixed
- POST запросы с form data теперь работают корректно через curl fallback
- Исправлена проблема с возвратом `None` для POST запросов при ошибках SSL

## [0.1.0] - 2025-12-04

### Added
- Начальная версия библиотеки
- Поддержка GET запросов через requests, pyOpenSSL и curl fallback
- Docker образ с предустановленным GOST engine
- Python библиотека `gost_http` для работы с GOST сайтами
- Примеры использования в директории `examples/`
- Тесты в директории `tests/`

