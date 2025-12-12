# Python с поддержкой GOST Cryptographic Engine

[![Docker Image Version](https://img.shields.io/docker/v/gseldon/python-gost-engine?sort=semver&logo=docker)](https://hub.docker.com/r/gseldon/python-gost-engine)

Docker образ и Python библиотека для работы с сайтами и сервисами, использующими российские криптографические стандарты GOST (GOST R 34.10-2012, GOST R 34.11-2012) в SSL/TLS соединениях.

## Docker Hub

Образ доступен на [Docker Hub](https://hub.docker.com/r/gseldon/python-gost-engine):

```bash
docker pull gseldon/python-gost-engine:latest
```

Или используйте конкретную версию:

```bash
docker pull gseldon/python-gost-engine:3.12-alpine-v0.1.0
```

Проект предоставляет готовое решение для разработчиков, которым необходимо работать с российскими сервисами, поддерживающими только GOST шифрование. Включает Docker образ с предустановленным Python и библиотеку `gost_http` для простой интеграции в существующие проекты.

## Быстрый старт

### Использование Docker

```bash
# Сборка образа
make build

# Запуск тестов
make test

# Запуск примеров
make example
```

Подробнее о работе с Docker см. в [Makefile](Makefile).

### Работа без Docker

#### Установка зависимостей

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential gcc g++ make cmake \
    libssl-dev libffi-dev \
    git wget python3 python3-pip
```

**Alpine Linux:**
```bash
apk add --no-cache \
    gcc g++ make cmake musl-dev openssl-dev \
    git wget python3 py3-pip
```

#### Установка GOST Engine

1. Клонируйте и соберите GOST engine:
```bash
cd /usr/local/src
sudo git clone --depth 1 https://github.com/gost-engine/engine.git
cd engine
sudo mkdir build && cd build
sudo cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DOPENSSL_ENGINES_DIR=/usr/lib/engines-3 \
    ..
sudo cmake --build . --parallel $(nproc)
sudo cmake --install .
```

2. Настройте OpenSSL:
```bash
sudo cp example.conf /etc/ssl/gost.cnf
sudo sed -i "s|dynamic_path\s*=.*$|dynamic_path = /usr/lib/engines-3/gost.so|" /etc/ssl/gost.cnf
sudo sed -i "11i .include /etc/ssl/gost.cnf" /etc/ssl/openssl.cnf
export OPENSSL_CONF=/etc/ssl/openssl.cnf
```

#### Установка Python библиотеки gost_http

```bash
# Установка зависимостей
pip install requests pyOpenSSL cryptography

# Установка gost_http (из исходников)
git clone https://github.com/your-repo/python-gost-engine.git
cd python-gost-engine
pip install -e .
```

#### Использование

```python
# Вариант 1: Замена импорта (самый простой)
from gost_http import requests_gost
requests = requests_gost.requests

# Теперь используйте requests как обычно
response = requests.get('https://dss.uc-em.ru/')
print(response.status_code)

# Вариант 2: Использование функций
from gost_http import gost_get

response = gost_get('https://dss.uc-em.ru/')
if response:
    print(f"Status: {response.status_code}")

# Вариант 3: Использование класса
from gost_http import GOSTHTTPClient

client = GOSTHTTPClient(verify=False, timeout=10)
response = client.get('https://dss.uc-em.ru/')

# POST запросы с form data
form_data = {
    'grant_type': 'password',
    'username': 'user@example.com',
    'password': 'password'
}
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic ...'
}
response = client.post('https://dss.uc-em.ru/STS/oauth/token', 
                       data=form_data, headers=headers)
if response:
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        token = response.json().get('access_token')
```

Подробнее о библиотеке `gost_http` см. в [gost_http/README.md](gost_http/README.md).

## Используемые проекты

- **[gost-engine](https://github.com/gost-engine/engine)** - Эталонная реализация криптографических алгоритмов GOST для OpenSSL
- **[Python](https://www.python.org/)** - Официальная дистрибуция Python (версия настраивается через ARG)
- **[Alpine Linux](https://alpinelinux.org/)** - Базовый образ Docker
- **[pyOpenSSL](https://github.com/pyca/pyopenssl)** - Python обертка для OpenSSL
- **[requests](https://github.com/psf/requests)** - HTTP библиотека для Python

## Структура проекта

```
python-gost-engine/
├── Dockerfile              # Многоэтапная сборка Docker образа
├── Makefile               # Автоматизация сборки и тестирования
├── README.md              # Этот файл
├── gost_http/             # Python библиотека для работы с GOST сайтами
│   ├── __init__.py
│   ├── gost_http_client.py
│   ├── requests_gost.py
│   └── README.md          # Подробная документация библиотеки
├── examples/              # Примеры использования
│   ├── gost_requests_simple.py
│   ├── gost_requests_session.py
│   └── gost_requests_wrapper.py
├── tests/                 # Тесты
│   └── test_gost_http.py
└── dev/                   # Документация разработки
    └── gost_engine_loading_options.md
```

## Возможности

- ✅ Поддержка российских криптографических стандартов GOST
- ✅ Автоматический выбор метода подключения (requests/pyOpenSSL/curl)
- ✅ Работа с сайтами только с GOST cipher suites
- ✅ Работа со смешанными сайтами (GOST + стандартные cipher suites)
- ✅ Поддержка всех HTTP методов (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
- ✅ POST запросы с form data и JSON данными
- ✅ Автоматический fallback на curl при ошибках SSL
- ✅ Простой API, совместимый с `requests`
- ✅ Docker образ с предустановленным окружением
- ✅ Python библиотека для интеграции в существующие проекты

## Поддерживаемые алгоритмы GOST

- **Подпись**: GOST R 34.10-2012 (256/512 бит)
- **Хэш**: GOST R 34.11-2012 (Streebog 256/512 бит)
- **Шифрование**: GOST 28147-89, Kuznyechik, Magma
- **Обмен ключами**: VKO GOST R 34.10-2012

## Примеры использования

См. директорию [examples/](examples/) для подробных примеров:

- `gost_requests_simple.py` - Простое использование функций
- `gost_requests_session.py` - Использование сессий
- `gost_requests_wrapper.py` - Замена импорта requests
- `gost_requests_post.py` - POST запросы с form data и JSON

## Тестирование

```bash
# В Docker
make test

# Без Docker
python3 tests/test_gost_http.py
```

## Документация

- [gost_http/README.md](gost_http/README.md) - Подробная документация библиотеки
- [dev/gost_engine_loading_options.md](dev/gost_engine_loading_options.md) - История разработки и различные подходы

## Лицензия

Этот проект следует лицензированию своих компонентов:
- GOST Engine: Apache 2.0 / OpenSSL License
- Python: PSF License
- Alpine Linux: Различные open-source лицензии

## Ссылки

- [Документация GOST Engine](https://github.com/gost-engine/engine)
- [Российские криптографические стандарты](https://tc26.ru/)
- [Документация OpenSSL](https://www.openssl.org/docs/)
- [Документация pyOpenSSL](https://www.pyopenssl.org/)
