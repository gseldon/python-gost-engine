#!/usr/bin/env python3
"""
Пример использования pyOpenSSL для работы с GOST сайтами через requests

Требования:
    pip install pyOpenSSL cryptography requests urllib3

Этот пример показывает, как явно загрузить GOST engine через pyOpenSSL
и использовать его с requests для подключения к сайтам, которые используют
только GOST cipher suites (например, dss.uc-em.ru).
"""

import os
import sys
import subprocess


def install_package(package):
    """Устанавливает пакет через pip"""
    try:
        print(f"Установка {package}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"✓ {package} установлен")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Не удалось установить {package}")
        return False
    except Exception as e:
        print(f"✗ Ошибка при установке {package}: {e}")
        return False


def check_and_install_dependencies():
    """Проверяет и устанавливает необходимые зависимости"""
    required_packages = {
        'pyOpenSSL': 'OpenSSL',
        'cryptography': 'cryptography',
        'requests': 'requests',
        'urllib3': 'urllib3'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("=" * 60)
        print("Обнаружены отсутствующие зависимости")
        print("=" * 60)
        print(f"Отсутствуют: {', '.join(missing_packages)}")
        print("\nПопытка автоматической установки...")
        print()
        
        all_installed = True
        for package in missing_packages:
            if not install_package(package):
                all_installed = False
        
        if not all_installed:
            print("\n✗ Не удалось установить все зависимости")
            print("Попробуйте установить вручную:")
            print(f"  pip install {' '.join(missing_packages)}")
            return False
        
        print("\n✓ Все зависимости установлены")
        print("=" * 60)
        print()
        
        # После установки нужно переимпортировать модули
        # Но это не всегда работает, поэтому просто возвращаем True
        # и надеемся, что импорт пройдет при следующей попытке
    
    return True


# Проверяем и устанавливаем зависимости перед импортом
if not check_and_install_dependencies():
    sys.exit(1)

try:
    from OpenSSL import SSL, crypto
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.contrib.pyopenssl import PyOpenSSLContext
    from urllib3.poolmanager import PoolManager
except ImportError as e:
    print(f"Ошибка импорта после установки зависимостей: {e}")
    print("\nПопробуйте установить вручную:")
    print("  pip install pyOpenSSL cryptography requests urllib3")
    sys.exit(1)


# Глобальная переменная для отслеживания загрузки GOST engine
_gost_engine_loaded = False

def load_gost_engine():
    """Загружает и инициализирует GOST engine через pyOpenSSL"""
    global _gost_engine_loaded
    
    # Если engine уже загружен, не загружаем повторно
    if _gost_engine_loaded:
        return True
    
    try:
        # Устанавливаем OPENSSL_CONF для загрузки конфигурации
        if 'OPENSSL_CONF' not in os.environ:
            os.environ['OPENSSL_CONF'] = '/etc/ssl/openssl.cnf'
        
        # Загружаем конфигурацию OpenSSL через ctypes (если доступно)
        try:
            import ctypes
            libcrypto = ctypes.CDLL('libcrypto.so.3')
            if hasattr(libcrypto, 'OPENSSL_config'):
                OPENSSL_config = libcrypto.OPENSSL_config
                OPENSSL_config.argtypes = [ctypes.c_char_p]
                OPENSSL_config.restype = ctypes.c_int
                OPENSSL_config(None)
        except Exception:
            pass  # Пропускаем, если не удалось загрузить конфигурацию
        
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
            print("GOST engine не найден")
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
            print("Не удалось инициализировать GOST engine")
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
        print("✓ GOST engine успешно загружен")
        return True
        
    except Exception as e:
        print(f"Ошибка при загрузке GOST engine: {e}")
        import traceback
        traceback.print_exc()
        return False


class GOSTAdapter(HTTPAdapter):
    """HTTPAdapter с поддержкой GOST через pyOpenSSL"""
    
    def init_poolmanager(self, *args, **kwargs):
        """Инициализирует pool manager с SSL контекстом, поддерживающим GOST"""
        # Загружаем GOST engine перед созданием контекста
        if not load_gost_engine():
            print("Предупреждение: GOST engine не загружен, соединение может не работать")
        
        # Используем pyOpenSSL контекст для urllib3
        # PyOpenSSLContext принимает протокол из стандартного модуля ssl, а не SSL.TLS_CLIENT_METHOD
        try:
            import ssl as std_ssl
            # PyOpenSSLContext принимает протокол из стандартного модуля ssl
            # Используем PROTOCOL_TLS_CLIENT (Python 3.6+) или PROTOCOL_TLS (для совместимости)
            try:
                # Пробуем использовать PROTOCOL_TLS_CLIENT (Python 3.6+)
                ssl_context = PyOpenSSLContext(std_ssl.PROTOCOL_TLS_CLIENT)
            except (KeyError, AttributeError):
                # Fallback на PROTOCOL_TLS для старых версий Python
                ssl_context = PyOpenSSLContext(std_ssl.PROTOCOL_TLS)
            ssl_context.load_default_certs()
            # Отключаем проверку сертификата
            ssl_context.check_hostname = False
            ssl_context.verify_mode = std_ssl.CERT_NONE
            
            # Пытаемся настроить cipher suites для поддержки GOST
            # Получаем внутренний SSL.Context из PyOpenSSLContext
            try:
                # PyOpenSSLContext имеет атрибут _ctx для доступа к внутреннему контексту
                if hasattr(ssl_context, '_ctx'):
                    ctx = ssl_context._ctx
                    # Пытаемся установить cipher list, включающий GOST
                    # Используем правильные имена cipher suites для OpenSSL 3.x
                    try:
                        # Пробуем установить cipher list с GOST (для TLS 1.2 и ниже)
                        # Используем правильные имена из openssl ciphers
                        ctx.set_cipher_list('GOST2012-KUZNYECHIK-KUZNYECHIKOMAC:GOST2012-GOST8912-GOST8912:GOST2001-GOST89-GOST89:ALL:!aNULL:!eNULL')
                    except Exception as e1:
                        # Если не работает, пробуем без явного указания GOST
                        try:
                            ctx.set_cipher_list('ALL:!aNULL:!eNULL')
                        except Exception as e2:
                            pass  # Игнорируем ошибки установки cipher list
            except Exception:
                pass  # Игнорируем ошибки настройки cipher suites
            
            kwargs['ssl_context'] = ssl_context
        except Exception as e:
            print(f"Предупреждение: не удалось создать SSL контекст через pyOpenSSL: {e}")
            # Пробуем использовать стандартный контекст
            import ssl as std_ssl
            ctx_std = std_ssl.create_default_context()
            ctx_std.check_hostname = False
            ctx_std.verify_mode = std_ssl.CERT_NONE
            kwargs['ssl_context'] = ctx_std
        
        return super().init_poolmanager(*args, **kwargs)


def test_gost_site(url):
    """Тестирует подключение к GOST сайту"""
    print(f"\nТестирование подключения к {url}...")
    
    # Сначала пробуем через прямой pyOpenSSL (для сайтов только с GOST)
    if url == 'dss.uc-em.ru':
        try:
            import socket as socket_module
            if load_gost_engine():
                ctx = SSL.Context(SSL.TLS_CLIENT_METHOD)
                ctx.set_verify(SSL.VERIFY_NONE, None)
                # Устанавливаем cipher list с GOST (используем правильные имена)
                try:
                    # Для TLS 1.2 используем правильные имена
                    ctx.set_cipher_list('GOST2012-KUZNYECHIK-KUZNYECHIKOMAC:GOST2012-GOST8912-GOST8912:GOST2001-GOST89-GOST89:ALL:!aNULL:!eNULL')
                except:
                    try:
                        ctx.set_cipher_list('ALL:!aNULL:!eNULL')
                    except:
                        pass
                
                sock = socket_module.socket(socket_module.AF_INET, socket_module.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((url, 443))
                ssl_sock = SSL.Connection(ctx, sock)
                ssl_sock.set_tlsext_host_name(url.encode())
                ssl_sock.do_handshake()
                
                # Получаем информацию о cipher
                cipher = ssl_sock.get_cipher()
                print(f"✓ Успешно подключено через прямой pyOpenSSL!")
                print(f"  Cipher: {cipher[0]}")
                print(f"  Version: {cipher[1]}")
                
                # Делаем простой HTTP запрос
                ssl_sock.send(b'GET / HTTP/1.1\r\nHost: ' + url.encode() + b'\r\nConnection: close\r\n\r\n')
                response_data = b''
                while True:
                    try:
                        data = ssl_sock.recv(4096)
                        if not data:
                            break
                        response_data += data
                    except:
                        break
                
                ssl_sock.close()
                sock.close()
                
                if b'HTTP' in response_data:
                    status_line = response_data.split(b'\r\n')[0].decode('utf-8', errors='ignore')
                    print(f"  HTTP ответ: {status_line}")
                    return True
        except Exception as e:
            print(f"Прямое подключение через pyOpenSSL не удалось: {e}")
    
    # Пробуем через requests с адаптером
    session = requests.Session()
    session.mount('https://', GOSTAdapter())
    
    try:
        response = session.get(f'https://{url}/', verify=False, timeout=10)
        print(f"✓ Успешно подключено! Статус: {response.status_code}")
        print(f"  Размер ответа: {len(response.content)} байт")
        return True
    except requests.exceptions.SSLError as e:
        print(f"✗ SSL ошибка: {e}")
        return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def get_cipher_info(url):
    """Получает информацию о cipher suite через pyOpenSSL"""
    print(f"\nПолучение информации о cipher suite для {url}...")
    
    try:
        import socket as socket_module
        
        # Загружаем GOST engine
        if not load_gost_engine():
            print("Не удалось загрузить GOST engine")
            return False
        
        # Создаем SSL контекст
        ctx = SSL.Context(SSL.TLS_CLIENT_METHOD)
        ctx.set_verify(SSL.VERIFY_NONE, None)
        
        # Создаем TCP соединение
        sock = socket_module.socket(socket_module.AF_INET, socket_module.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((url, 443))
        
        # Создаем SSL соединение
        ssl_sock = SSL.Connection(ctx, sock)
        ssl_sock.set_tlsext_host_name(url.encode())
        
        # Выполняем handshake
        ssl_sock.do_handshake()
        
        # Получаем информацию о cipher
        cipher = ssl_sock.get_cipher()
        print(f"✓ Cipher: {cipher[0]}")
        print(f"  Version: {cipher[1]}")
        print(f"  Bits: {cipher[2]}")
        
        # Проверяем наличие GOST в cipher
        if 'GOST' in cipher[0].upper() or 'KUZNYECHIK' in cipher[0].upper():
            print("  ✓ GOST cipher suite обнаружен!")
        else:
            print("  ⚠ GOST cipher suite не обнаружен")
        
        # Получаем сертификат
        cert = ssl_sock.get_peer_certificate()
        if cert:
            subject = cert.get_subject()
            print(f"  Certificate Subject: {subject}")
        
        ssl_sock.close()
        sock.close()
        return True
        
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Пример использования pyOpenSSL с GOST engine")
    print("=" * 60)
    
    # Тестируем подключение к GOST сайтам
    gost_sites = ['dss.uc-em.ru', 'cryptopro.ru']
    
    results = []
    for site in gost_sites:
        success = test_gost_site(site)
        results.append((site, success))
    
    print("\n" + "=" * 60)
    print("Результаты тестирования:")
    print("=" * 60)
    for site, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {site}")
    
    # Показываем информацию о cipher для успешных подключений
    print("\n" + "=" * 60)
    print("Информация о cipher suite:")
    print("=" * 60)
    for site, success in results:
        if success:
            get_cipher_info(site)

