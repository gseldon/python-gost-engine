# Python с GOST Cryptographic Engine

Docker образ с Python, собранным на базе OpenSSL с поддержкой криптографических алгоритмов GOST.

## Цель и назначение проекта

Проект предназначен для работы с сайтами и сервисами, которые поддерживают только российский криптографический стандарт GOST SSL/TLS. Основные сценарии использования:

- Реализация API клиентов для работы с российскими сервисами, использующими только GOST шифрование
- Обращение к сайтам, поддерживающим исключительно GOST SSL/TLS
- Разработка приложений, требующих поддержку российских криптографических стандартов
- Интеграция с системами, работающими по ГОСТ стандартам

## Обзор

Этот проект предоставляет Python окружение с полной поддержкой российских криптографических стандартов GOST (GOST R 34.10-2012, GOST R 34.11-2012) через интеграцию с OpenSSL GOST engine.

## Источники

- **GOST Engine**: [gost-engine](https://github.com/gost-engine/engine) - Эталонная реализация криптографических алгоритмов GOST для OpenSSL
- **Python**: [CPython 3.12.0](https://www.python.org/downloads/release/python-3120/) - Официальная дистрибуция Python
- **Базовый образ**: Alpine Linux (оптимизированная сборка GOST engine)

## Возможности

- ✅ Python 3.12.0 скомпилирован с OpenSSL 3.5.4
- ✅ Полная поддержка криптографии GOST
- ✅ Предустановленные пакеты: `requests`, `urllib3`
- ✅ Утилиты: `curl`, `gostsum`, `gost12sum`
- ✅ Оптимизированная многоэтапная сборка
- ✅ Небольшой размер образа: ~312MB

## Поддерживаемые алгоритмы GOST

- **Подпись**: GOST R 34.10-2012 (256/512 бит)
- **Хэш**: GOST R 34.11-2012 (Streebog 256/512 бит)
- **Шифрование**: GOST 28147-89, Kuznyechik, Magma
- **Обмен ключами**: VKO GOST R 34.10-2012

## Сборка

### Предварительные требования

1. Соберите базовый образ GOST engine:
```bash
cd ../engine
docker build -f docker/Dockerfile.alpine -t engine:alpine-optimized .
```

2. Соберите образ Python:
```bash
cd python-gost-engine
docker build -t python-gost-engine:latest .
```

### Аргументы сборки

- `PYTHON_VERSION` - Версия Python для сборки (по умолчанию: 3.12.0)
- `GOST_ENGINE_REPO` - URL репозитория GOST engine (по умолчанию: https://github.com/gost-engine/engine)
- `GOST_ENGINE_BRANCH` - Ветка или тег GOST engine (по умолчанию: master)

Пример:
```bash
docker build --build-arg PYTHON_VERSION=3.11.10 -t python-gost-engine:3.11 .
docker build --build-arg GOST_ENGINE_BRANCH=v3.0.0 -t python-gost-engine:latest .
```

## Использование

### Базовое использование Python

```bash
# Запустить интерпретатор Python
docker run --rm -it python-gost-engine python3

# Проверить версию Python
docker run --rm python-gost-engine python3 --version

# Проверить версию OpenSSL
docker run --rm python-gost-engine python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

### Запуск скриптов

```bash
# Запустить Python скрипт
docker run --rm -v $(pwd):/app python-gost-engine python3 script.py

# Интерактивный режим с монтированием тома
docker run --rm -it -v $(pwd):/app python-gost-engine bash
```

### Доступ к сайтам с защитой GOST

Из-за ограничений модуля SSL Python с GOST, используйте `curl` через subprocess:

```python
import subprocess
import html

# Доступ к сайту с защитой GOST
result = subprocess.run(
    ["curl", "-k", "-L", "-s", "https://example-gost-site.ru/"],
    capture_output=True,
    text=True
)

content = html.unescape(result.stdout)
print(content)
```

См. директорию `examples/` для дополнительных примеров.

## Тестирование

Запустите набор тестов:

```bash
# Запустить все тесты
docker run --rm -v $(pwd)/tests:/tests python-gost-engine python3 -m pytest /tests

# Запустить конкретный тест
docker run --rm python-gost-engine python3 tests/test_gost.py
```

## Архитектура

### Многоэтапная сборка

1. **Этап сборки**: 
   - Устанавливает зависимости для сборки
   - Компилирует Python из исходников с поддержкой OpenSSL GOST
   - Устанавливает Python пакеты

2. **Финальный этап**:
   - Минимальные зависимости для выполнения
   - Копирует скомпилированный Python и библиотеки
   - Настроенный GOST engine

### Структура директорий

```
python-gost-engine/
├── Dockerfile           # Определение многоэтапной сборки
├── README.md           # Этот файл
├── tests/              # Набор тестов
│   ├── test_gost.py   # Тесты функциональности GOST
│   └── test_ssl.py    # Тесты SSL/TLS
└── examples/          # Примеры использования
    ├── basic_usage.py
    ├── gost_site.py
    └── certificate_check.py
```

## Переменные окружения

- `LD_LIBRARY_PATH=/usr/local/lib` - Путь к разделяемым библиотекам Python
- `OPENSSL_CONF=/etc/ssl/openssl.cnf` - Конфигурация OpenSSL с GOST engine

## Ограничения

- Прямые HTTPS запросы через модуль `ssl` Python к сайтам только с GOST требуют дополнительной настройки SSL контекста
- Рекомендуемый подход: Использовать `subprocess` с `curl` для сайтов с GOST
- Некоторые Python пакеты могут не работать с сертификатами GOST без пользовательских адаптеров

## Производительность

- **Время сборки**: ~6 минут (с оптимизациями)
- **Размер образа**: 312 MB
- **Базовый образ**: 12.8 MB (оптимизированный GOST engine)

## Вопросы безопасности

- Собран с `--enable-optimizations` для использования в продакшене
- Использует официальные исходники Python с проверкой контрольных сумм
- GOST engine из официального репозитория
- Рекомендуются регулярные обновления безопасности

## Устранение неполадок

### Проблемы с модулем SSL Python

Если вы столкнулись с ошибками SSL на сайтах с GOST:
```python
# Используйте subprocess с curl вместо этого
import subprocess
result = subprocess.run(['curl', '-k', 'https://site.ru'], capture_output=True)
```

### Ошибки "Модуль не найден"

Убедитесь, что `LD_LIBRARY_PATH` установлен:
```bash
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

## Участие в разработке

Вклад в проект приветствуется! Пожалуйста:
1. Сделайте fork репозитория
2. Создайте ветку для новой функции
3. Добавьте тесты для новой функциональности
4. Отправьте pull request

## Лицензия

Этот проект следует лицензированию своих компонентов:
- GOST Engine: Apache 2.0 / OpenSSL License
- Python: PSF License
- Alpine Linux: Различные open-source лицензии

## Ссылки

- [Документация GOST Engine](https://github.com/gost-engine/engine)
- [Российские криптографические стандарты](https://tc26.ru/)
- [Документация OpenSSL](https://www.openssl.org/docs/)
- [Модуль SSL Python](https://docs.python.org/3/library/ssl.html)
- [Рекомендации TK26 по TLS](https://cryptopro.ru/sites/default/files/products/tls/tk26tls.pdf) - Рекомендации по использованию алгоритмов шифрования GOST 28147-89 в протоколе TLS
- [TLS 1.2 и новый GOST (Habr)](https://habr.com/ru/articles/339978/) - Обзор криптографических алгоритмов GOST в протоколе TLS 1.2

## История версий

- **1.0.0** - Первый релиз с Python 3.12.0 и OpenSSL 3.5.4
