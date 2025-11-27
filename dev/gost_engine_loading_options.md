# Варианты загрузки GOST engine в Python

## Текущая проблема

Python `ssl` модуль не использует GOST engine автоматически при создании SSL контекста через `ssl.create_default_context()`, даже если:
- GOST engine установлен и доступен (`openssl engine -t gost` показывает `available`)
- Конфигурация OpenSSL настроена правильно (`OPENSSL_CONF=/etc/ssl/openssl.cnf`)
- `curl` и `openssl s_client` успешно работают с GOST сайтами

**Причина:** Python `ssl` модуль создает свой собственный `SSL_CTX` при вызове `ssl.create_default_context()`, который не наследует загруженный GOST engine из глобального контекста OpenSSL.

**Следствие:**
- `curl` и `openssl s_client` работают с GOST сайтами (например, `dss.uc-em.ru`)
- `requests.get()` и Python `ssl` модуль не могут подключиться к сайтам, которые используют только GOST cipher suites
- Для смешанных сайтов (например, `cryptopro.ru`) `requests.get()` работает, но может использовать не-GOST cipher

## Варианты решения

### 1. Через ctypes (прямой доступ к libcrypto)

**Описание:** Прямой вызов функций OpenSSL через ctypes для загрузки engine до создания SSL контекста.

**Реализация:**
```python
import ctypes
libcrypto = ctypes.CDLL('libcrypto.so.3')

ENGINE_load_builtin_engines = libcrypto.ENGINE_load_builtin_engines
ENGINE_load_builtin_engines.restype = ctypes.c_int

ENGINE_by_id = libcrypto.ENGINE_by_id
ENGINE_by_id.argtypes = [ctypes.c_char_p]
ENGINE_by_id.restype = ctypes.c_void_p

ENGINE_init = libcrypto.ENGINE_init
ENGINE_init.argtypes = [ctypes.c_void_p]
ENGINE_init.restype = ctypes.c_int

ENGINE_set_default = libcrypto.ENGINE_set_default
ENGINE_set_default.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
ENGINE_set_default.restype = ctypes.c_int

# Загрузка engine
ENGINE_load_builtin_engines()
engine = ENGINE_by_id(b'gost')
if engine:
    ENGINE_init(engine)
    ENGINE_set_default(engine, 0xFFFF)  # ALL
```

**Плюсы:**
- Не требует дополнительных библиотек
- Работает со стандартным Python ssl
- Полный контроль над процессом загрузки

**Минусы:**
- ❌ **Не решает проблему:** Python ssl создает новый SSL_CTX, который не наследует загруженный engine
- Требует знания внутренностей OpenSSL API
- Сложно поддерживать

**Статус:** Реализовано, но не работает для Python ssl модуля

---

### 2. Через pyOpenSSL (текущий подход)

**Описание:** Использование pyOpenSSL для создания SSL контекста с загруженным GOST engine.

**Реализация:**
```python
from OpenSSL import SSL
from urllib3.contrib.pyopenssl import PyOpenSSLContext
import ssl as std_ssl

# Загрузка GOST engine
def load_gost_engine():
    SSL._lib.ENGINE_load_builtin_engines()
    engine = SSL._lib.ENGINE_by_id(b'gost')
    if engine:
        SSL._lib.ENGINE_init(engine)
        SSL._lib.ENGINE_set_default(engine, 0xFFFF)
        return True
    return False

# Создание контекста
load_gost_engine()
ssl_context = PyOpenSSLContext(std_ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = std_ssl.CERT_NONE
```

**Плюсы:**
- Более высокоуровневый API
- Интеграция с requests через urllib3
- Работает для прямых SSL соединений через `SSL.Connection`

**Минусы:**
- Требует установки `pyOpenSSL` и `cryptography`
- `PyOpenSSLContext` не всегда корректно использует загруженный engine
- Может не работать с requests в некоторых случаях
- Для сайтов только с GOST нужно использовать прямой `SSL.Connection` вместо requests

**Статус:** Частично реализовано в `examples/pyopenssl_gost.py`

---

### 3. Модификация SSL контекста через ctypes после создания

**Описание:** Создание SSL контекста через Python ssl, затем модификация через ctypes для добавления GOST engine.

**Реализация:**
```python
import ssl
import ctypes

ctx = ssl.create_default_context()
# Пробуем получить внутренний SSL_CTX через ctypes
# и добавить GOST engine
```

**Плюсы:**
- Использует стандартный Python ssl
- Может работать с requests

**Минусы:**
- ❌ Сложно получить доступ к внутреннему SSL_CTX из Python ssl
- ❌ Может не работать из-за инкапсуляции в Python
- Требует глубокого знания внутренностей Python

**Статус:** Не реализовано, сложно

---

### 4. Патч Python ssl модуля при импорте

**Описание:** Монки-патчинг функций создания SSL контекста для автоматической загрузки GOST engine.

**Реализация:**
```python
import ssl
original_create_default_context = ssl.create_default_context

def patched_create_default_context():
    # Загружаем GOST engine
    load_gost_engine()
    # Вызываем оригинальную функцию
    ctx = original_create_default_context()
    # Пытаемся модифицировать контекст
    # ...
    return ctx

ssl.create_default_context = patched_create_default_context
```

**Плюсы:**
- Прозрачно для пользователя
- Работает автоматически

**Минусы:**
- ❌ Сложно реализовать
- ❌ Может сломаться при обновлении Python
- ❌ Требует глубокого понимания внутренностей Python ssl
- ❌ Не решает проблему с созданием нового SSL_CTX

**Статус:** Не реализовано, рискованно

---

### 5. Использование SSL_CTX_set_cipher_list с GOST cipher suites

**Описание:** Установка cipher list с GOST cipher suites в SSL контексте через ctypes.

**Реализация:**
```python
import ssl
import ctypes

ctx = ssl.create_default_context()
# Пробуем установить cipher list через ctypes
libssl = ctypes.CDLL('libssl.so.3')
# Получаем внутренний SSL_CTX и устанавливаем cipher list
```

**Плюсы:**
- Может работать, если engine уже загружен глобально
- Не требует изменения структуры контекста

**Минусы:**
- ❌ Не работает, если engine не загружен в контекст
- ❌ Cipher suites могут быть недоступны без engine
- ❌ Сложно получить доступ к внутреннему SSL_CTX

**Статус:** Не реализовано, маловероятно что сработает

---

### 6. Загрузка engine через переменные окружения и конфигурацию

**Описание:** Использование OPENSSL_CONF и автоматической загрузки при инициализации OpenSSL.

**Реализация:**
```bash
export OPENSSL_CONF=/etc/ssl/openssl.cnf
```

**Плюсы:**
- Простота настройки
- Работает для curl/openssl

**Минусы:**
- ❌ Не работает для Python ssl (не читает конфигурацию автоматически)
- Требует дополнительных действий

**Статус:** Уже настроено в Dockerfile, но не помогает для Python ssl

---

### 7. Создание кастомного SSL контекста через ctypes

**Описание:** Полное создание SSL контекста через ctypes с загруженным GOST engine, затем обертка для Python.

**Реализация:**
```python
import ctypes
libssl = ctypes.CDLL('libssl.so.3')
libcrypto = ctypes.CDLL('libcrypto.so.3')

# Создаем SSL_CTX через ctypes
SSL_CTX_new = libssl.SSL_CTX_new
# Загружаем GOST engine
# Создаем обертку для Python
```

**Плюсы:**
- Полный контроль
- Может работать с requests через кастомный адаптер

**Минусы:**
- ❌ Очень сложно реализовать
- ❌ Требует глубокого знания OpenSSL API
- ❌ Много кода для поддержки
- ❌ Сложная интеграция с Python ssl

**Статус:** Не реализовано, очень сложно

---

### 8. Использование SSL_CTX_set_client_cert_cb и callback функций

**Описание:** Использование callback функций OpenSSL для загрузки GOST engine при создании соединения.

**Реализация:**
```python
import ctypes
libssl = ctypes.CDLL('libssl.so.3')

# Создаем callback функцию
def load_gost_callback(ssl, ctx, userdata):
    # Загружаем GOST engine
    pass

# Устанавливаем callback
SSL_CTX_set_client_cert_cb = libssl.SSL_CTX_set_client_cert_cb
```

**Плюсы:**
- Может работать автоматически
- Интеграция на уровне OpenSSL

**Минусы:**
- ❌ Сложно реализовать
- ❌ Требует доступа к внутренним структурам Python ssl
- ❌ Callback функции не решают проблему с созданием нового SSL_CTX

**Статус:** Не реализовано, сложно

---

## Текущее решение

### Для сайтов только с GOST (dss.uc-em.ru)

**Использовать прямой SSL.Connection через pyOpenSSL:**

```python
from OpenSSL import SSL
import socket

load_gost_engine()  # Загружаем GOST engine
ctx = SSL.Context(SSL.TLS_CLIENT_METHOD)
ctx.set_verify(SSL.VERIFY_NONE, None)
ctx.set_cipher_list('GOST2012-KUZNYECHIK-KUZNYECHIKOMAC:...')

sock = socket.create_connection(('dss.uc-em.ru', 443), timeout=10)
ssl_sock = SSL.Connection(ctx, sock)
ssl_sock.set_tlsext_host_name('dss.uc-em.ru')
ssl_sock.do_handshake()
# Работа с соединением
```

**Или использовать subprocess с curl:**
```python
import subprocess
result = subprocess.run(['curl', '-k', 'https://dss.uc-em.ru/'], 
                       capture_output=True, text=True)
```

### Для смешанных сайтов (cryptopro.ru)

**Использовать стандартный requests.get():**
```python
import requests
response = requests.get('https://cryptopro.ru', verify=False, timeout=10)
# Работает, но может использовать не-GOST cipher
```

---

## Рекомендации

1. **Для универсального решения:** Комбинировать подходы:
   - Пробовать прямой `SSL.Connection` через pyOpenSSL для сайтов только с GOST
   - Fallback на стандартный `requests.get()` для смешанных сайтов

2. **Для продакшена:** Использовать `subprocess` с `curl` для критичных GOST сайтов

3. **Для разработки:** Использовать `pyOpenSSL` с прямым `SSL.Connection` для тестирования

4. **Долгосрочное решение:** Рассмотреть создание Python C extension для загрузки GOST engine в SSL контекст

---

## Альтернативные варианты (не реализованы)

### Создание Python C extension

**Описание:** Создание C extension модуля, который загружает GOST engine при инициализации Python ssl.

**Плюсы:**
- Может работать автоматически
- Интеграция на уровне C кода
- Высокая производительность

**Минусы:**
- ❌ Очень сложно реализовать
- ❌ Требует компиляции C кода
- ❌ Сложно поддерживать

### Использование библиотеки sslpsk

**Описание:** Использование библиотеки для кастомных SSL контекстов.

**Плюсы:**
- Готовая библиотека
- Может поддерживать кастомные контексты

**Минусы:**
- ❌ Неизвестно, поддерживает ли GOST engine
- ❌ Дополнительная зависимость

### Создание wrapper библиотеки

**Описание:** Создание библиотеки, которая перехватывает создание SSL контекстов.

**Плюсы:**
- Может работать прозрачно
- Переиспользуемый код

**Минусы:**
- ❌ Сложно реализовать
- ❌ Требует поддержки

---

## Выводы

**Основная проблема:** Python `ssl` модуль создает новый `SSL_CTX` при каждом вызове `ssl.create_default_context()`, который не наследует загруженный GOST engine из глобального контекста OpenSSL.

**Текущее рабочее решение:**
- Для сайтов только с GOST: использовать прямой `SSL.Connection` через pyOpenSSL или `subprocess` с `curl`
- Для смешанных сайтов: использовать стандартный `requests.get()`

**Потенциальные улучшения:**
- Создание Python C extension для автоматической загрузки GOST engine
- Модификация Python ssl модуля (требует пересборки Python)
- Использование альтернативных библиотек для SSL

---

## Ссылки

- [Документация GOST Engine](https://github.com/gost-engine/engine)
- [Python ssl модуль](https://docs.python.org/3/library/ssl.html)
- [pyOpenSSL документация](https://www.pyopenssl.org/en/stable/)
- [OpenSSL Engine API](https://www.openssl.org/docs/man3.0/man3/ENGINE_load_builtin_engines.html)

