# GOST HTTP Client - Python wrapper библиотека

Универсальный HTTP клиент для работы с GOST сайтами, который автоматически выбирает правильный метод подключения.

## Возможности

- Автоматический выбор метода подключения (requests/pyOpenSSL/curl)
- Поддержка сайтов только с GOST cipher suites
- Поддержка смешанных сайтов (GOST + обычные cipher suites)
- Graceful degradation при ошибках
- Простой API, совместимый с requests

## Установка

```bash
# Установка зависимостей
pip install requests pyOpenSSL cryptography
```

## Использование

### Простое использование

```python
from gost_http import gost_get

# Автоматически выберет правильный метод подключения
response = gost_get('https://dss.uc-em.ru/')
if response:
    print(f"Status: {response.status_code}")
    print(f"Content: {response.text[:100]}")
```

### Использование сессии

```python
from gost_http import gost_session

session = gost_session(timeout=10)
response = session.get('https://dss.uc-em.ru/')
if response:
    print(response.status_code)
```

### Использование класса

```python
from gost_http import GOSTHTTPClient

client = GOSTHTTPClient(verify=False, timeout=10)
response = client.get('https://dss.uc-em.ru/')
if response:
    print(response.status_code)
    print(response.text)
```

## Как это работает

1. **Первый шаг:** Пробует стандартный `requests.get()` (работает для смешанных сайтов)
2. **При SSL ошибке:** Пробует `pyOpenSSL` через requests adapter (для сайтов только с GOST)
3. **При ошибке:** Пробует прямой `SSL.Connection` через pyOpenSSL (критичные случаи)
4. **Fallback:** Использует `subprocess` с `curl` (последний вариант)

## Примеры

### Подключение к сайту только с GOST

```python
from gost_http import gost_get

response = gost_get('https://dss.uc-em.ru/')
if response:
    print(f"Успешно подключено! Status: {response.status_code}")
else:
    print("Не удалось подключиться")
```

### Подключение к смешанному сайту

```python
from gost_http import gost_get

response = gost_get('https://cryptopro.ru/')
if response:
    print(f"Status: {response.status_code}")
```

## Требования

- Python 3.6+
- requests
- pyOpenSSL
- cryptography
- curl (для fallback)

## Лицензия

Apache-2.0

