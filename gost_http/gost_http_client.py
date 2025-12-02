#!/usr/bin/env python3
"""
GOST HTTP Client - универсальный HTTP клиент для работы с GOST сайтами

Автоматически определяет метод подключения:
1. Пробует стандартный requests.get() (для смешанных сайтов)
2. При ошибке SSL пробует pyOpenSSL (для сайтов только с GOST)
3. При ошибке пробует subprocess с curl (fallback)
"""

import os
import sys
import socket
import subprocess
from typing import Optional, Dict, Any, Union
from urllib.parse import urlparse

try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests import Response, Session
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    Response = None
    Session = None

try:
    from OpenSSL import SSL
    from urllib3.contrib.pyopenssl import PyOpenSSLContext
    import ssl as std_ssl
    PYOPENSSL_AVAILABLE = True
except ImportError:
    PYOPENSSL_AVAILABLE = False
    SSL = None
    PyOpenSSLContext = None
    std_ssl = None

# Глобальная переменная для отслеживания загрузки GOST engine
_gost_engine_loaded = False


def load_gost_engine() -> bool:
    """
    Загружает GOST engine через pyOpenSSL
    
    Returns:
        bool: True если engine успешно загружен, False в противном случае
    """
    global _gost_engine_loaded
    
    if _gost_engine_loaded:
        return True
    
    if not PYOPENSSL_AVAILABLE:
        return False
    
    try:
        # Устанавливаем OPENSSL_CONF для загрузки конфигурации
        if 'OPENSSL_CONF' not in os.environ:
            os.environ['OPENSSL_CONF'] = '/etc/ssl/openssl.cnf'
        
        # Загружаем встроенные engines
        if hasattr(SSL._lib, 'ENGINE_load_builtin_engines'):
            SSL._lib.ENGINE_load_builtin_engines()
        else:
            # Альтернативный способ через ctypes
            import ctypes
            libcrypto = ctypes.CDLL('libcrypto.so.3')
            ENGINE_load_builtin_engines = libcrypto.ENGINE_load_builtin_engines
            ENGINE_load_builtin_engines.restype = ctypes.c_int
            ENGINE_load_builtin_engines()
        
        # Находим GOST engine
        if hasattr(SSL._lib, 'ENGINE_by_id'):
            engine = SSL._lib.ENGINE_by_id(b'gost')
        else:
            # Альтернативный способ через ctypes
            import ctypes
            libcrypto = ctypes.CDLL('libcrypto.so.3')
            ENGINE_by_id = libcrypto.ENGINE_by_id
            ENGINE_by_id.argtypes = [ctypes.c_char_p]
            ENGINE_by_id.restype = ctypes.c_void_p
            engine = ENGINE_by_id(b'gost')
        
        if not engine:
            return False
        
        # Инициализируем engine
        if hasattr(SSL._lib, 'ENGINE_init'):
            init_result = SSL._lib.ENGINE_init(engine)
        else:
            import ctypes
            libcrypto = ctypes.CDLL('libcrypto.so.3')
            ENGINE_init = libcrypto.ENGINE_init
            ENGINE_init.argtypes = [ctypes.c_void_p]
            ENGINE_init.restype = ctypes.c_int
            init_result = ENGINE_init(engine)
        
        if init_result != 1:
            return False
        
        # Устанавливаем engine по умолчанию для всех алгоритмов
        if hasattr(SSL._lib, 'ENGINE_set_default'):
            SSL._lib.ENGINE_set_default(engine, 0xFFFF)  # ALL
        else:
            import ctypes
            libcrypto = ctypes.CDLL('libcrypto.so.3')
            ENGINE_set_default = libcrypto.ENGINE_set_default
            ENGINE_set_default.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
            ENGINE_set_default.restype = ctypes.c_int
            ENGINE_set_default(engine, 0xFFFF)
        
        _gost_engine_loaded = True
        return True
        
    except Exception:
        return False


class GOSTAdapter(HTTPAdapter):
    """HTTPAdapter с поддержкой GOST через pyOpenSSL"""
    
    def init_poolmanager(self, *args, **kwargs):
        """Инициализирует pool manager с SSL контекстом, поддерживающим GOST"""
        if not PYOPENSSL_AVAILABLE:
            return super().init_poolmanager(*args, **kwargs)
        
        # Загружаем GOST engine перед созданием контекста
        load_gost_engine()
        
        try:
            # Используем pyOpenSSL контекст для urllib3
            try:
                ssl_context = PyOpenSSLContext(std_ssl.PROTOCOL_TLS_CLIENT)
            except (KeyError, AttributeError):
                ssl_context = PyOpenSSLContext(std_ssl.PROTOCOL_TLS)
            
            ssl_context.load_default_certs()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = std_ssl.CERT_NONE
            
            # Пытаемся настроить cipher suites для поддержки GOST
            try:
                if hasattr(ssl_context, '_ctx'):
                    ctx = ssl_context._ctx
                    try:
                        ctx.set_cipher_list('GOST2012-KUZNYECHIK-KUZNYECHIKOMAC:GOST2012-GOST8912-GOST8912:GOST2001-GOST89-GOST89:ALL:!aNULL:!eNULL')
                    except Exception:
                        try:
                            ctx.set_cipher_list('ALL:!aNULL:!eNULL')
                        except Exception:
                            pass
            except Exception:
                pass
            
            kwargs['ssl_context'] = ssl_context
        except Exception:
            # Fallback на стандартный контекст
            import ssl as std_ssl
            ctx_std = std_ssl.create_default_context()
            ctx_std.check_hostname = False
            ctx_std.verify_mode = std_ssl.CERT_NONE
            kwargs['ssl_context'] = ctx_std
        
        return super().init_poolmanager(*args, **kwargs)


def _connect_via_pyopenssl(hostname: str, port: int = 443, timeout: int = 10) -> Optional[SSL.Connection]:
    """
    Подключается к хосту через прямой pyOpenSSL SSL.Connection
    
    Args:
        hostname: Имя хоста
        port: Порт (по умолчанию 443)
        timeout: Таймаут в секундах
    
    Returns:
        SSL.Connection или None при ошибке
    """
    if not PYOPENSSL_AVAILABLE:
        return None
    
    try:
        if not load_gost_engine():
            return None
        
        ctx = SSL.Context(SSL.TLS_CLIENT_METHOD)
        ctx.set_verify(SSL.VERIFY_NONE, None)
        
        # Устанавливаем cipher list с GOST
        try:
            ctx.set_cipher_list('GOST2012-KUZNYECHIK-KUZNYECHIKOMAC:GOST2012-GOST8912-GOST8912:GOST2001-GOST89-GOST89:ALL:!aNULL:!eNULL')
        except Exception:
            try:
                ctx.set_cipher_list('ALL:!aNULL:!eNULL')
            except Exception:
                pass
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((hostname, port))
        
        ssl_sock = SSL.Connection(ctx, sock)
        ssl_sock.set_tlsext_host_name(hostname.encode())
        ssl_sock.do_handshake()
        
        return ssl_sock
        
    except Exception:
        return None


def _fetch_via_curl(url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Получает содержимое URL через subprocess с curl
    
    Args:
        url: URL для получения
        timeout: Таймаут в секундах
    
    Returns:
        Словарь с 'status_code', 'content', 'headers' или None при ошибке
    """
    try:
        result = subprocess.run(
            ['curl', '-k', '-L', '-s', '--connect-timeout', str(timeout), url],
            capture_output=True,
            text=True,
            timeout=timeout + 5
        )
        
        if result.returncode == 0:
            return {
                'status_code': 200,
                'content': result.stdout,
                'headers': {},
                'text': result.stdout
            }
        return None
    except Exception:
        return None


class GOSTHTTPClient:
    """
    Универсальный HTTP клиент для работы с GOST сайтами
    
    Автоматически выбирает метод подключения:
    1. Стандартный requests.get() (для смешанных сайтов)
    2. pyOpenSSL через requests adapter (для сайтов только с GOST)
    3. Прямой pyOpenSSL SSL.Connection (для критичных случаев)
    4. subprocess с curl (fallback)
    """
    
    def __init__(self, verify: bool = False, timeout: int = 10):
        """
        Инициализирует клиент
        
        Args:
            verify: Проверять ли SSL сертификаты (по умолчанию False)
            timeout: Таймаут запросов в секундах
        """
        self.verify = verify
        self.timeout = timeout
        self.session = None
        
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            if PYOPENSSL_AVAILABLE:
                # Используем GOST adapter для всех HTTPS соединений
                self.session.mount('https://', GOSTAdapter())
    
    def _request(self, method: str, url: str, **kwargs) -> Optional[Response]:
        """
        Универсальный метод для выполнения HTTP запросов
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
            url: URL для запроса
            **kwargs: Дополнительные аргументы для requests
        
        Returns:
            Response объект или None при ошибке
        """
        if not REQUESTS_AVAILABLE:
            # Для curl fallback поддерживаем только GET
            if method.upper() == 'GET':
                return self._get_via_curl(url)
            return None
        
        # Пробуем стандартный requests через session
        try:
            response = self.session.request(
                method,
                url,
                verify=self.verify if 'verify' not in kwargs else kwargs.pop('verify', self.verify),
                timeout=kwargs.pop('timeout', self.timeout),
                **kwargs
            )
            # Принимаем успешные статусы
            if response.status_code in [200, 201, 202, 204, 301, 302, 303, 307, 308]:
                return response
            # Для других методов принимаем любые статусы
            if method.upper() != 'GET':
                return response
        except requests.exceptions.SSLError:
            # SSL ошибка - для методов кроме GET используем только session с GOST adapter
            # (прямой pyOpenSSL сложен для POST/PUT с телом запроса)
            if method.upper() != 'GET':
                # Пробуем еще раз через session (с GOST adapter уже установлен)
                try:
                    return self.session.request(
                        method,
                        url,
                        verify=False,
                        timeout=kwargs.pop('timeout', self.timeout),
                        **kwargs
                    )
                except Exception:
                    return None
        except Exception:
            pass
        
        # Для GET пробуем прямой pyOpenSSL (как в текущей реализации)
        if method.upper() == 'GET':
            parsed = urlparse(url)
            if parsed.scheme == 'https':
                hostname = parsed.hostname
                port = parsed.port or 443
                path = parsed.path or '/'
                
                ssl_sock = _connect_via_pyopenssl(hostname, port, self.timeout)
                if ssl_sock:
                    try:
                        request = f'GET {path} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n'
                        ssl_sock.send(request.encode())
                        
                        response_data = b''
                        while True:
                            try:
                                data = ssl_sock.recv(4096)
                                if not data:
                                    break
                                response_data += data
                            except Exception:
                                break
                        
                        ssl_sock.close()
                        
                        if b'HTTP' in response_data:
                            class MockResponse:
                                def __init__(self, content, status_code=200):
                                    self.content = content
                                    self.text = content.decode('utf-8', errors='ignore')
                                    self.status_code = status_code
                                    self.headers = {}
                            
                            return MockResponse(response_data, 200)
                    except Exception:
                        pass
            
            # Fallback на curl для GET
            return self._get_via_curl(url)
        
        return None
    
    def get(self, url: str, **kwargs) -> Optional[Response]:
        """Выполняет GET запрос"""
        return self._request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> Optional[Response]:
        """Выполняет POST запрос"""
        return self._request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> Optional[Response]:
        """Выполняет PUT запрос"""
        return self._request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Optional[Response]:
        """Выполняет DELETE запрос"""
        return self._request('DELETE', url, **kwargs)
    
    def patch(self, url: str, **kwargs) -> Optional[Response]:
        """Выполняет PATCH запрос"""
        return self._request('PATCH', url, **kwargs)
    
    def head(self, url: str, **kwargs) -> Optional[Response]:
        """Выполняет HEAD запрос"""
        return self._request('HEAD', url, **kwargs)
    
    def options(self, url: str, **kwargs) -> Optional[Response]:
        """Выполняет OPTIONS запрос"""
        return self._request('OPTIONS', url, **kwargs)
    
    def _get_via_curl(self, url: str) -> Optional[Response]:
        """Получает содержимое через curl"""
        result = _fetch_via_curl(url, self.timeout)
        if result:
            class MockResponse:
                def __init__(self, content, status_code, text):
                    self.content = content.encode() if isinstance(content, str) else content
                    self.text = text
                    self.status_code = status_code
                    self.headers = {}
            
            return MockResponse(result['content'], result['status_code'], result['text'])
        return None


def gost_get(url: str, verify: bool = False, timeout: int = 10, **kwargs) -> Optional[Response]:
    """GET запрос с поддержкой GOST"""
    client = GOSTHTTPClient(verify=verify, timeout=timeout)
    return client.get(url, **kwargs)

def gost_post(url: str, verify: bool = False, timeout: int = 10, **kwargs) -> Optional[Response]:
    """POST запрос с поддержкой GOST"""
    client = GOSTHTTPClient(verify=verify, timeout=timeout)
    return client.post(url, **kwargs)

def gost_put(url: str, verify: bool = False, timeout: int = 10, **kwargs) -> Optional[Response]:
    """PUT запрос с поддержкой GOST"""
    client = GOSTHTTPClient(verify=verify, timeout=timeout)
    return client.put(url, **kwargs)

def gost_delete(url: str, verify: bool = False, timeout: int = 10, **kwargs) -> Optional[Response]:
    """DELETE запрос с поддержкой GOST"""
    client = GOSTHTTPClient(verify=verify, timeout=timeout)
    return client.delete(url, **kwargs)

def gost_patch(url: str, verify: bool = False, timeout: int = 10, **kwargs) -> Optional[Response]:
    """PATCH запрос с поддержкой GOST"""
    client = GOSTHTTPClient(verify=verify, timeout=timeout)
    return client.patch(url, **kwargs)

def gost_head(url: str, verify: bool = False, timeout: int = 10, **kwargs) -> Optional[Response]:
    """HEAD запрос с поддержкой GOST"""
    client = GOSTHTTPClient(verify=verify, timeout=timeout)
    return client.head(url, **kwargs)

def gost_options(url: str, verify: bool = False, timeout: int = 10, **kwargs) -> Optional[Response]:
    """OPTIONS запрос с поддержкой GOST"""
    client = GOSTHTTPClient(verify=verify, timeout=timeout)
    return client.options(url, **kwargs)

def gost_session(verify: bool = False, timeout: int = 10) -> GOSTHTTPClient:
    """
    Создает сессию GOST HTTP клиента
    
    Args:
        verify: Проверять ли SSL сертификаты
        timeout: Таймаут в секундах
    
    Returns:
        GOSTHTTPClient объект
    
    Example:
        >>> session = gost_session()
        >>> response = session.get('https://dss.uc-em.ru/')
    """
    return GOSTHTTPClient(verify=verify, timeout=timeout)

