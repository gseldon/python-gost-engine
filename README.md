# Python с поддержкой GOST Cryptographic Engine

Docker образ с модифицированным Python, собранным на базе OpenSSL с поддержкой криптографических алгоритмов GOST.

## Цель и назначение проекта

Проект описывает модификацию Python и его использование в Docker для работы с сайтами и сервисами, которые поддерживают только российский криптографический стандарт GOST SSL/TLS. Основные сценарии использования:

- Реализация API клиентов для работы с российскими сервисами, использующими только GOST шифрование
- Обращение к сайтам, поддерживающим исключительно GOST SSL/TLS
- Разработка приложений, требующих поддержку российских криптографических стандартов
- Интеграция с системами, работающими по ГОСТ стандартам

## Обзор

Этот проект предоставляет Python окружение с полной поддержкой российских криптографических стандартов GOST (GOST R 34.10-2012, GOST R 34.11-2012) через интеграцию с OpenSSL GOST engine.

Проект использует [gost-engine](https://github.com/gost-engine/engine) как источник кода для реализации криптографических алгоритмов GOST. Python компилируется из исходников с поддержкой OpenSSL, в который интегрирован GOST engine, что позволяет использовать российские криптографические стандарты в Python приложениях, запущенных в Docker контейнере.

## Источники

- **GOST Engine**: [gost-engine](https://github.com/gost-engine/engine) - Эталонная реализация криптографических алгоритмов GOST для OpenSSL
- **Python**: [CPython 3.12.0](https://www.python.org/downloads/release/python-3120/) - Официальная дистрибуция Python
- **Базовый образ**: Alpine Linux

## Возможности

- ✅ Python 3.12.0 скомпилирован с OpenSSL 3.5.4
- ✅ Полная поддержка криптографии GOST
- ✅ Предустановленные пакеты: `requests`, `urllib3`
- ✅ Оптимизированная многоэтапная сборка
- ✅ Небольшой размер образа: ~433MB

## Поддерживаемые алгоритмы GOST

- **Подпись**: GOST R 34.10-2012 (256/512 бит)
- **Хэш**: GOST R 34.11-2012 (Streebog 256/512 бит)
- **Шифрование**: GOST 28147-89, Kuznyechik, Magma
- **Обмен ключами**: VKO GOST R 34.10-2012

## Сборка

### Сборка с использованием Docker

#### Сборка образа

Соберите образ Python:
```bash
cd python-gost-engine
docker build -t python-gost-engine:latest .
```

#### Аргументы сборки

- `PYTHON_VERSION` - Версия Python для сборки (по умолчанию: 3.12.0)
- `GOST_ENGINE_REPO` - URL репозитория GOST engine (по умолчанию: https://github.com/gost-engine/engine)
- `GOST_ENGINE_BRANCH` - Ветка или тег GOST engine (по умолчанию: master)

Пример:
```bash
docker build --build-arg PYTHON_VERSION=3.11.10 -t python-gost-engine:3.11 .
docker build --build-arg GOST_ENGINE_BRANCH=v3.0.0 -t python-gost-engine:latest .
```

### Сборка на Ubuntu (без Docker)

Если Docker не требуется, можно собрать Python с поддержкой GOST напрямую на Ubuntu.

#### Предварительные требования

Установите необходимые зависимости:
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    libssl-dev \
    libbz2-dev \
    libexpat1-dev \
    libgdbm-dev \
    libffi-dev \
    libncurses5-dev \
    libreadline-dev \
    libsqlite3-dev \
    liblzma-dev \
    zlib1g-dev \
    wget \
    git \
    cmake \
```

#### Сборка GOST Engine

1. Клонируйте репозиторий gost-engine:
```bash
cd /usr/local/src
sudo git clone --depth 1 https://github.com/gost-engine/engine.git
cd engine
```

2. Соберите и установите GOST engine:
```bash
sudo mkdir build && cd build
sudo cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON \
    -DOPENSSL_ENGINES_DIR=/usr/lib/x86_64-linux-gnu/engines-3 \
    ..
sudo cmake --build . --parallel $(nproc) --target install
sudo cp bin/gostsum bin/gost12sum /usr/local/bin
```

3. Настройте OpenSSL для использования GOST engine:
```bash
sudo cp example.conf /etc/ssl/gost.cnf
sudo sed -i "s|dynamic_path\s*=.*$|dynamic_path = /usr/lib/x86_64-linux-gnu/engines-3/gost.so|" /etc/ssl/gost.cnf
sudo sed -i "11i .include /etc/ssl/gost.cnf" /etc/ssl/openssl.cnf
```

#### Сборка Python

1. Скачайте и распакуйте исходники Python:
```bash
cd /usr/local/src
PYTHON_VERSION=3.12.0
sudo wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz
sudo tar -xf Python-${PYTHON_VERSION}.tar.xz
cd Python-${PYTHON_VERSION}
```

2. Соберите Python с поддержкой OpenSSL и GOST:
```bash
sudo ./configure \
    --prefix=/usr/local \
    --enable-optimizations \
    --with-openssl=/usr \
    --with-openssl-rpath=auto \
    --enable-shared \
    LDFLAGS="-Wl,-rpath /usr/local/lib"

sudo make -j $(nproc)
sudo make install
```

3. Настройте переменные окружения:
```bash
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
export OPENSSL_CONF=/etc/ssl/openssl.cnf
```

4. Установите дополнительные пакеты (опционально):
```bash
/usr/local/bin/python3 -m pip install --upgrade pip
/usr/local/bin/python3 -m pip install requests urllib3
```

5. Проверьте установку:
```bash
/usr/local/bin/python3 --version
/usr/local/bin/python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"
openssl engine -t gost
```

**Примечание**: После сборки убедитесь, что `/usr/local/bin` находится в `PATH`, или используйте полный путь к Python.

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

### Использование requests для работы с сайтами

Для работы с сайтами используйте библиотеку `requests`:

```python
import requests

# Запрос к сайту
response = requests.get('https://example.com', verify=False, timeout=10)
print(response.status_code)
print(response.text)
```

См. директорию `examples/` для дополнительных примеров.

## Тестирование

Запустите набор тестов:

```bash
# Запустить тесты с requests.get()
docker run --rm -v $(pwd)/tests:/app/tests python-gost-engine python3 /app/tests/test_requests.py

# Запустить тесты SSL/TLS
docker run --rm -v $(pwd)/tests:/app/tests python-gost-engine python3 /app/tests/test_ssl.py

# Запустить тесты GOST функциональности
docker run --rm -v $(pwd)/tests:/app/tests python-gost-engine python3 /app/tests/test_gost.py
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
│   ├── test_ssl.py    # Тесты SSL/TLS
│   └── test_requests.py  # Тесты с requests.get()
└── examples/          # Примеры использования
    ├── basic_usage.py
    ├── gost_site.py
    ├── certificate_check.py
    └── pyopenssl_gost.py  # Пример использования pyOpenSSL с GOST engine
```

## Переменные окружения

- `LD_LIBRARY_PATH=/usr/local/lib` - Путь к разделяемым библиотекам Python
- `OPENSSL_CONF=/etc/ssl/openssl.cnf` - Конфигурация OpenSSL с GOST engine

## Ограничения

- **Python ssl модуль не использует GOST engine автоматически**: 
  - Python был собран с `--with-openssl=/usr`, что означает использование системного OpenSSL с поддержкой GOST engine
  - Однако Python `ssl` модуль создает свой собственный SSL_CTX при вызове `ssl.create_default_context()`, который не наследует загруженный GOST engine
  - В отличие от `curl` и `openssl s_client`, которые автоматически читают `OPENSSL_CONF` и загружают GOST engine при запуске
  - Это означает, что:
    - `curl` и `openssl s_client` работают с GOST сайтами (например, `dss.uc-em.ru`)
    - `requests.get()` и Python `ssl` модуль не могут подключиться к сайтам, которые используют только GOST cipher suites, даже если GOST engine загружен через ctypes
    - Для работы с такими сайтами через Python требуется использование `subprocess` с `curl` или использование `pyOpenSSL` для создания SSL контекста с явной загрузкой GOST engine
- Прямые HTTPS запросы через модуль `ssl` Python к сайтам только с GOST требуют дополнительной настройки SSL контекста
- Некоторые Python пакеты могут не работать с сертификатами GOST без пользовательских адаптеров

## Производительность

- **Время сборки**: ~6 минут (с оптимизациями)
- **Размер образа**: ~433 MB

## Вопросы безопасности

- Собран с `--enable-optimizations` для использования в продакшене
- Использует официальные исходники Python с проверкой контрольных сумм
- GOST engine из официального репозитория
- Рекомендуются регулярные обновления безопасности

## Устранение неполадок

### Проблемы с модулем SSL Python

**Почему curl работает, а requests.get() нет?**

`curl` и `openssl s_client` автоматически читают `OPENSSL_CONF` и загружают GOST engine при запуске. Python `ssl` модуль не делает этого автоматически при создании SSL контекста, поэтому не может использовать GOST cipher suites.

**Решения:**

1. **Использовать subprocess с curl** (рекомендуется для сайтов только с GOST):
```python
import subprocess
result = subprocess.run(['curl', '-k', 'https://dss.uc-em.ru/'], 
                       capture_output=True, text=True)
```

2. **Использовать pyOpenSSL для явной загрузки GOST engine**:
```python
# Требует установки: pip install pyOpenSSL cryptography
from OpenSSL import SSL
import requests
from requests.adapters import HTTPAdapter
from urllib3.contrib.pyopenssl import PyOpenSSLContext

def load_gost_engine():
    """Загружает GOST engine через pyOpenSSL"""
    SSL._lib.OPENSSL_config(None)  # Загружает OPENSSL_CONF
    SSL._lib.ENGINE_load_builtin_engines()
    engine = SSL._lib.ENGINE_by_id(b'gost')
    if engine:
        SSL._lib.ENGINE_init(engine)
        SSL._lib.ENGINE_set_default(engine, 0xFFFF)  # ALL
        return True
    return False

class GOSTAdapter(HTTPAdapter):
    """HTTPAdapter с поддержкой GOST"""
    def init_poolmanager(self, *args, **kwargs):
        load_gost_engine()  # Загружаем GOST engine
        ctx = SSL.Context(SSL.TLS_CLIENT_METHOD)
        ctx.set_verify(SSL.VERIFY_NONE, None)
        kwargs['ssl_context'] = PyOpenSSLContext(ctx)
        return super().init_poolmanager(*args, **kwargs)

session = requests.Session()
session.mount('https://', GOSTAdapter())
response = session.get('https://dss.uc-em.ru/', verify=False, timeout=10)
print(f"Status: {response.status_code}")
```

Полный рабочий пример см. в `examples/pyopenssl_gost.py`

3. **Для сайтов, которые поддерживают обычные и GOST cipher suites** (например, `cryptopro.ru`):
```python
# requests.get() работает, но может использовать не-GOST cipher
import requests
response = requests.get('https://cryptopro.ru', verify=False, timeout=10)
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
