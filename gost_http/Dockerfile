# Dockerfile для сборки образа с gost_http wrapper библиотекой
ARG BASE_IMAGE=python-gost-engine:latest

FROM ${BASE_IMAGE}

# Устанавливаем зависимости для gost_http
RUN python3 -m pip install --no-cache-dir \
    requests \
    pyOpenSSL \
    cryptography

# Копируем gost_http библиотеку
COPY gost_http/ /usr/local/lib/python3.12/site-packages/gost_http/

# Проверяем установку
RUN python3 -c "import gost_http; print('✓ gost_http installed successfully')" && \
    python3 -c "from gost_http import gost_get, gost_session, GOSTHTTPClient; print('✓ All imports work')"

WORKDIR /app

LABEL maintainer="36692159+gseldon@users.noreply.github.com"
LABEL description="Python with GOST HTTP wrapper library"
LABEL python.version="3.12.0"
LABEL wrapper.version="0.1.0"

