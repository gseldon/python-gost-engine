FROM alpine:latest AS builder

RUN apk update \
    && apk add --no-cache --virtual .build-deps \
      gcc \
      g++ \
      make \
      cmake \
      musl-dev \
      openssl-dev \
      openssl \
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

ARG PYTHON_VERSION=3.12.0
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
    && cd /usr/local/src

# Configure OpenSSL for GOST engine
RUN mkdir -p /etc/ssl \
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
    fi

# Build Python with GOST support
RUN wget --no-check-certificate https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz \
    && tar -xf Python-${PYTHON_VERSION}.tar.xz \
    && cd Python-${PYTHON_VERSION} \
    && ./configure \
        --prefix=/usr/local \
        --enable-optimizations \
        --with-openssl=/usr \
        --with-openssl-rpath=auto \
        --enable-shared \
        LDFLAGS="-Wl,-rpath /usr/local/lib" \
    && make -j $(nproc) \
    && make install \
    && cd / \
    && rm -rf /usr/local/src/Python-${PYTHON_VERSION}*

RUN python3 -m pip install --no-cache-dir requests urllib3

FROM alpine:latest

RUN apk update \
    && apk add --no-cache \
      curl \
      openssl \
      libffi \
      expat \
      gdbm \
      readline \
      sqlite-libs \
      xz-libs \
      bzip2 \
      ncurses-libs \
    && rm -rf /var/cache/apk/*

COPY --from=builder /usr/local/ /usr/local/

# Copy GOST engine files and configuration
RUN mkdir -p /usr/lib/engines-3 /etc/ssl
COPY --from=builder /usr/lib/engines-3/ /usr/lib/engines-3/
COPY --from=builder /etc/ssl/gost.cnf /etc/ssl/gost.cnf

# Ensure OpenSSL configuration includes GOST engine
RUN if [ -f /etc/ssl/openssl.cnf ] && ! grep -q "gost.cnf" /etc/ssl/openssl.cnf; then \
        sed -i "11i .include /etc/ssl/gost.cnf" /etc/ssl/openssl.cnf || true; \
    fi

RUN ln -sf /usr/local/bin/python3 /usr/local/bin/python \
    && ln -sf /usr/local/bin/pip3 /usr/local/bin/pip

ENV LD_LIBRARY_PATH=/usr/local/lib
ENV OPENSSL_CONF=/etc/ssl/openssl.cnf

WORKDIR /app

LABEL maintainer="36692159+gseldon@users.noreply.github.com"
LABEL description="Python with GOST cryptographic support for OpenSSL"
LABEL python.version="3.12.0"
LABEL openssl.version="3.5.4"




