FROM engine:alpine-optimized AS builder

RUN apk update \
    && apk add --no-cache --virtual .build-deps \
      gcc \
      g++ \
      make \
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
      wget

ARG PYTHON_VERSION=3.12.8

WORKDIR /usr/local/src

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

FROM engine:alpine-optimized

RUN apk update \
    && apk add --no-cache \
      curl \
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

RUN ln -sf /usr/local/bin/python3 /usr/local/bin/python \
    && ln -sf /usr/local/bin/pip3 /usr/local/bin/pip

ENV LD_LIBRARY_PATH=/usr/local/lib
ENV OPENSSL_CONF=/etc/ssl/openssl.cnf

WORKDIR /app

LABEL maintainer="GOST Engine Community"
LABEL description="Python with GOST cryptographic support for OpenSSL"
LABEL python.version="3.12.8"
LABEL openssl.version="3.5.4"




