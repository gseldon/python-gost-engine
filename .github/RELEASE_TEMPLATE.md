# Release v{VERSION}

**Дата релиза:** {DATE}

## Описание

Этот релиз содержит обновления Docker образа Python с поддержкой криптографических алгоритмов GOST.

## Основные изменения

- {Описание новой функциональности 1}
- {Описание новой функциональности 2}

## Улучшения

- {Описание улучшения 1}
- {Описание улучшения 2}

## Исправления ошибок

- {Описание исправления 1}
- {Описание исправления 2}

## Технические детали

### Версии компонентов

- **Python:** {PYTHON_VERSION}
- **Alpine Linux:** {ALPINE_VERSION}
- **GOST HTTP Library:** v{GOST_HTTP_VERSION}
- **OpenSSL:** {OPENSSL_VERSION}
- **GOST Engine:** {GOST_ENGINE_VERSION}

### Docker образ

**Тег образа:** `{PYTHON_VERSION}-alpine-v{GOST_HTTP_VERSION}`

**Пример использования:**
```bash
docker pull {DOCKERHUB_USERNAME}/python-gost-engine:{PYTHON_VERSION}-alpine-v{GOST_HTTP_VERSION}
docker run --rm {DOCKERHUB_USERNAME}/python-gost-engine:{PYTHON_VERSION}-alpine-v{GOST_HTTP_VERSION} python3 --version
```

**Также доступен тег:** `latest`

## Использование

### Базовое использование

```bash
# Запуск Python интерпретатора
docker run --rm -it {DOCKERHUB_USERNAME}/python-gost-engine:{PYTHON_VERSION}-alpine-v{GOST_HTTP_VERSION} python3

# Проверка версии Python
docker run --rm {DOCKERHUB_USERNAME}/python-gost-engine:{PYTHON_VERSION}-alpine-v{GOST_HTTP_VERSION} python3 --version

# Проверка версии OpenSSL
docker run --rm {DOCKERHUB_USERNAME}/python-gost-engine:{PYTHON_VERSION}-alpine-v{GOST_HTTP_VERSION} python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

### Запуск скриптов

```bash
# Запуск Python скрипта
docker run --rm -v $(pwd):/app {DOCKERHUB_USERNAME}/python-gost-engine:{PYTHON_VERSION}-alpine-v{GOST_HTTP_VERSION} python3 script.py
```

## Поддерживаемые алгоритмы GOST

- **Подпись:** GOST R 34.10-2012 (256/512 бит)
- **Хэш:** GOST R 34.11-2012 (Streebog 256/512 бит)
- **Шифрование:** GOST 28147-89, Kuznyechik, Magma
- **Обмен ключами:** VKO GOST R 34.10-2012

## Изменения в сборке

- {Описание изменений в процессе сборки, если есть}

## Благодарности

- [gost-engine](https://github.com/gost-engine/engine) - за реализацию криптографических алгоритмов GOST
- [Python](https://www.python.org/) - за официальную дистрибуцию Python

## Полный список изменений

См. [CHANGELOG](https://github.com/{REPO_OWNER}/{REPO_NAME}/compare/{PREVIOUS_TAG}...{CURRENT_TAG}) для полного списка изменений.

---

**Скачать:** [Docker Hub](https://hub.docker.com/r/{DOCKERHUB_USERNAME}/python-gost-engine/tags)

