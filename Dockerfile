ARG ALPINE_VERSION=3
ARG PYTHON_VERSION=3.12

# Базовая стадия с общими runtime пакетами
FROM alpine:${ALPINE_VERSION} AS base
# apk update без удаления кеша для переиспользования между стадиями
RUN apk update && apk add --no-cache \
      openssl \
      libffi \
      expat \
      gdbm \
      readline \
      sqlite-libs \
      xz-libs \
      bzip2 \
      ncurses-libs

# Builder стадия для сборки
FROM base AS builder
# Установка build-зависимостей
RUN apk add --no-cache --virtual .build-deps \
      gcc \
      g++ \
      make \
      cmake \
      musl-dev \
      openssl-dev \
      bzip2-dev \
      expat-dev \
      gdbm-dev \
      libffi-dev \
      ncurses-dev \
      readline-dev \
      sqlite-dev \
      xz-dev \
      zlib-dev \
      wget \
      git \
      linux-headers

ARG GOST_ENGINE_REPO=https://github.com/gost-engine/engine
ARG GOST_ENGINE_BRANCH=master

WORKDIR /usr/local/src

# Clone and build GOST engine sources
RUN git clone --recursive --depth 1 --branch ${GOST_ENGINE_BRANCH} ${GOST_ENGINE_REPO}.git engine-sources \
    && cd engine-sources \
    && git submodule update --init --recursive --depth 1 \
    && rm -rf .git \
    && mkdir build && cd build \
    && cmake \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON \
        -DOPENSSL_ENGINES_DIR=/usr/lib/engines-3 \
        .. \
    && cmake --build . --parallel $(nproc) \
    && cmake --install . \
    && cp bin/gostsum bin/gost12sum /usr/local/bin/ 2>/dev/null || true \
    && cd /usr/local/src \
    && mkdir -p /etc/ssl \
    && if [ -f /usr/local/src/engine-sources/example.conf ]; then \
        cp /usr/local/src/engine-sources/example.conf /etc/ssl/gost.cnf; \
        sed -i "s|dynamic_path\s*=.*$|dynamic_path = /usr/lib/engines-3/gost.so|" /etc/ssl/gost.cnf || true; \
    elif [ -f /usr/local/src/engine-sources/build/example.conf ]; then \
        cp /usr/local/src/engine-sources/build/example.conf /etc/ssl/gost.cnf; \
        sed -i "s|dynamic_path\s*=.*$|dynamic_path = /usr/lib/engines-3/gost.so|" /etc/ssl/gost.cnf || true; \
    else \
        echo "# GOST Engine Configuration" > /etc/ssl/gost.cnf; \
        echo "openssl_conf = openssl_init" >> /etc/ssl/gost.cnf; \
        echo "" >> /etc/ssl/gost.cnf; \
        echo "[openssl_init]" >> /etc/ssl/gost.cnf; \
        echo "engines = engine_section" >> /etc/ssl/gost.cnf; \
        echo "" >> /etc/ssl/gost.cnf; \
        echo "[engine_section]" >> /etc/ssl/gost.cnf; \
        echo "gost = gost_section" >> /etc/ssl/gost.cnf; \
        echo "" >> /etc/ssl/gost.cnf; \
        echo "[gost_section]" >> /etc/ssl/gost.cnf; \
        echo "dynamic_path = /usr/lib/engines-3/gost.so" >> /etc/ssl/gost.cnf; \
        echo "default_algorithms = ALL" >> /etc/ssl/gost.cnf; \
    fi \
    && if [ -f /etc/ssl/openssl.cnf ] && ! grep -q "gost.cnf" /etc/ssl/openssl.cnf; then \
        sed -i "11i .include /etc/ssl/gost.cnf" /etc/ssl/openssl.cnf || true; \
    fi \
    && rm -rf engine-sources

# Финальная стадия - используем официальный образ Python
FROM python:${PYTHON_VERSION}-alpine AS final

# Объявляем ARG для финальной стадии (не наследуются автоматически)
ARG ALPINE_VERSION=3
ARG OPENSSL_VERSION
ARG GOST_HTTP_VERSION=0.1.0

# Установка runtime зависимостей и очистка кеша только в финальной стадии
RUN apk add --no-cache curl openssl \
    && rm -rf /var/cache/apk/*

# Копирование GOST engine из builder
COPY --from=builder /usr/lib/engines-3/ /usr/lib/engines-3/
COPY --from=builder /etc/ssl/gost.cnf /etc/ssl/gost.cnf

# Настройка OpenSSL конфигурации
RUN mkdir -p /usr/lib/engines-3 /etc/ssl \
    && if [ -f /etc/ssl/openssl.cnf ] && ! grep -q "gost.cnf" /etc/ssl/openssl.cnf; then \
        sed -i "11i .include /etc/ssl/gost.cnf" /etc/ssl/openssl.cnf || true; \
    fi

ENV OPENSSL_CONF=/etc/ssl/openssl.cnf

# Установка Python пакетов (pyOpenSSL, cryptography, requests, urllib3)
# Определяем версию pyOpenSSL для LABEL
RUN python3 -m pip install --no-cache-dir \
    requests \
    urllib3 \
    pyOpenSSL \
    cryptography \
    && python3 -c "import OpenSSL; print(OpenSSL.__version__)" > /tmp/pyopenssl_version.txt

# Установка gost_http библиотеки и проверка
ARG GOST_HTTP_VERSION
ENV GOST_HTTP_VERSION=${GOST_HTTP_VERSION}
COPY gost_http/ /tmp/gost_http/
RUN PYTHON_SITE_PACKAGES=$(python3 -c "import site; print(site.getsitepackages()[0])") && \
    echo "Python site-packages: $PYTHON_SITE_PACKAGES" && \
    mkdir -p "$PYTHON_SITE_PACKAGES" && \
    cp -r /tmp/gost_http "$PYTHON_SITE_PACKAGES/" && \
    rm -rf /tmp/gost_http && \
    echo "Installed gost_http version: $GOST_HTTP_VERSION" && \
    python3 -c "import gost_http; print('✓ gost_http installed successfully')" && \
    python3 -c "from gost_http import requests_gost; print('✓ requests_gost imported successfully')"

WORKDIR /app

LABEL maintainer="36692159+gseldon@users.noreply.github.com"
LABEL description="Python with GOST cryptographic support for OpenSSL"
LABEL alpine.version="${ALPINE_VERSION}"
LABEL gost_http.version="${GOST_HTTP_VERSION}"