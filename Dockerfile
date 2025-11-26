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
      wget \
      git

ARG PYTHON_VERSION=3.12.0
ARG GOST_ENGINE_REPO=https://github.com/gost-engine/engine
ARG GOST_ENGINE_BRANCH=master

WORKDIR /usr/local/src

# Clone GOST engine sources
RUN git clone --depth 1 --branch ${GOST_ENGINE_BRANCH} ${GOST_ENGINE_REPO}.git engine-sources \
    && rm -rf engine-sources/.git

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

LABEL maintainer="36692159+gseldon@users.noreply.github.com"
LABEL description="Python with GOST cryptographic support for OpenSSL"
LABEL python.version="3.12.0"
LABEL openssl.version="3.5.4"




