#!/usr/bin/env python3
"""
Тесты для gost_http wrapper библиотеки
"""

import sys
import warnings
from urllib3.exceptions import InsecureRequestWarning
from typing import Dict, Optional, Tuple

warnings.filterwarnings('ignore', category=InsecureRequestWarning)

GOST_SITES = ['dss.uc-em.ru', 'cryptopro.ru']
STANDARD_SITES = ['github.com']  # Сайты со стандартными cipher suites (не GOST)

# Глобальный словарь для хранения информации о SSL соединениях
ssl_info: Dict[str, Dict] = {}


def get_ssl_info(hostname: str, port: int = 443) -> Optional[Dict]:
    """
    Получает информацию о SSL соединении: cipher suite
    Использует curl для получения информации о cipher suite
    
    Args:
        hostname: Имя хоста
        port: Порт (по умолчанию 443)
    
    Returns:
        Словарь с информацией о cipher suite и сертификате или None
    """
    import subprocess
    import re
    
    try:
        # Используем curl для получения информации о сертификате
        cmd = [
            'curl', '-v', '--insecure',
            '--cacert', '/dev/null',
            f'https://{hostname}:{port}/',
            '-o', '/dev/null',
            '-s', '--max-time', '10'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=15
        )
        
        # curl выводит информацию в stderr
        output = result.stderr.decode('utf-8', errors='ignore')
        
        # Парсим cipher suite из вывода curl
        # Формат: "SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256 / x25519 / id-ecPublicKey"
        cipher_match = re.search(r'SSL connection using\s+(\S+)\s+/\s+(\S+)', output)
        if cipher_match:
            cipher_version = cipher_match.group(1)
            cipher_name = cipher_match.group(2)
        else:
            # Альтернативный формат: "SSL connection using TLSv1.3 TLS_AES_128_GCM_SHA256"
            cipher_match = re.search(r'SSL connection using\s+(\S+)\s+(\S+)', output)
            if cipher_match:
                cipher_version = cipher_match.group(1)
                cipher_name = cipher_match.group(2)
            else:
                # Ищем паттерны типа "Cipher: TLS_AES_256_GCM_SHA384"
                cipher_match = re.search(r'Cipher:\s*(\S+)', output, re.IGNORECASE)
                if cipher_match:
                    cipher_name = cipher_match.group(1)
                else:
                    # Ищем стандартные cipher suites в формате TLS_* или ECDHE-*
                    standard_cipher_match = re.search(r'(TLS_[A-Z0-9_]+|ECDHE-[A-Z0-9-]+|AES[0-9-]+)', output, re.IGNORECASE)
                    if standard_cipher_match:
                        cipher_name = standard_cipher_match.group(1)
                    else:
                        # Ищем GOST cipher suites
                        gost_cipher_match = re.search(r'(\S+GOST\S+)', output)
                        cipher_name = gost_cipher_match.group(1) if gost_cipher_match else "Unknown"
                cipher_version = "TLS"  # По умолчанию
        
        # Парсим версию TLS
        tls_match = re.search(r'(TLSv[\d.]+)', output)
        if tls_match:
            cipher_version = tls_match.group(1)
        
        # Пытаемся найти более точное название cipher из вывода
        # Ищем GOST cipher suites в выводе
        is_gost = False
        gost_cipher_patterns = [
            r'GOST2012-KUZNYECHIK-KUZNYECHIKOMAC',
            r'GOST2012-GOST8912-GOST8912',
            r'GOST2001-GOST89-GOST89',
            r'GOST[\w-]+',
        ]
        
        for pattern in gost_cipher_patterns:
            gost_match = re.search(pattern, output, re.IGNORECASE)
            if gost_match:
                cipher_name = gost_match.group(0)
                is_gost = True
                break
        
        # Определяем битность и тип cipher из названия
        cipher_bits = "Unknown"
        cipher_name_upper = cipher_name.upper()
        
        if is_gost or 'GOST' in cipher_name_upper:
            is_gost = True
            # GOST2012-KUZNYECHIK использует 256-битный ключ
            if 'KUZNYECHIK' in cipher_name_upper:
                cipher_bits = "256"
            # GOST2012-GOST8912 также использует 256-битный ключ
            elif 'GOST8912' in cipher_name_upper or 'GOST2012' in cipher_name_upper:
                cipher_bits = "256"
            # GOST2001-GOST89 использует 256-битный ключ
            elif 'GOST2001' in cipher_name_upper or 'GOST89' in cipher_name_upper:
                cipher_bits = "256"
            else:
                cipher_bits = "256"  # GOST обычно 256-битный
        else:
            # Определяем битность для стандартных cipher suites
            if 'AES_256' in cipher_name_upper or 'AES256' in cipher_name_upper:
                cipher_bits = "256"
            elif 'AES_128' in cipher_name_upper or 'AES128' in cipher_name_upper:
                cipher_bits = "128"
            elif '256' in cipher_name:
                cipher_bits = "256"
            elif '128' in cipher_name:
                cipher_bits = "128"
        
        return {
            'cipher_name': cipher_name,
            'cipher_version': cipher_version,
            'cipher_bits': cipher_bits,
            'is_gost': is_gost
        }
    except Exception:
        # Тихо игнорируем ошибки
        return None


def test_import_module():
    """Тест импорта модуля"""
    print("Тестирование импорта модуля gost_http...")
    try:
        import gost_http
        print(f"  ✓ Модуль успешно импортирован")
        print(f"  ✓ Версия: {gost_http.__version__}")
        return True, gost_http
    except ImportError as e:
        print(f"  ✗ Ошибка импорта: {e}")
        return False, None
    except Exception as e:
        print(f"  ✗ Неожиданная ошибка: {e}")
        return False, None


def test_gost_get_function(url):
    """Тест функции gost_get()"""
    print(f"Тестирование gost_get() для {url}...")
    try:
        from gost_http import gost_get
        
        response = gost_get(f'https://{url}/', timeout=10)
        
        if response and hasattr(response, 'status_code'):
            print(f"  ✓ Успешно подключено! Статус: {response.status_code}")
            if hasattr(response, 'text'):
                print(f"    Размер ответа: {len(response.text)} символов")
            return True
        else:
            print(f"  ✗ Не удалось получить ответ")
            return False
    except Exception as e:
        print(f"  ✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gost_session(url):
    """Тест использования сессии"""
    print(f"Тестирование gost_session() для {url}...")
    try:
        from gost_http import gost_session
        
        session = gost_session(timeout=10)
        response = session.get(f'https://{url}/')
        
        if response and hasattr(response, 'status_code'):
            print(f"  ✓ Успешно подключено! Статус: {response.status_code}")
            return True
        else:
            print(f"  ✗ Не удалось получить ответ")
            return False
    except Exception as e:
        print(f"  ✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gost_http_client(url):
    """Тест использования класса GOSTHTTPClient"""
    print(f"Тестирование GOSTHTTPClient для {url}...")
    try:
        from gost_http import GOSTHTTPClient
        
        client = GOSTHTTPClient(verify=False, timeout=10)
        
        # Тест GET
        response = client.get(f'https://{url}/')
        if response and hasattr(response, 'status_code'):
            print(f"  ✓ GET успешно! Статус: {response.status_code}")
        else:
            print(f"  ✗ GET не удалось")
            return False
        
        # Тест HEAD
        response = client.head(f'https://{url}/')
        if response and hasattr(response, 'status_code'):
            print(f"  ✓ HEAD успешно! Статус: {response.status_code}")
        
        # POST/PUT/DELETE требуют реальный API endpoint, пропускаем
        
        return True
    except Exception as e:
        print(f"  ✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_requests_gost(url):
    """Тест использования requests_gost"""
    print(f"Тестирование requests_gost для {url}...")
    try:
        from gost_http import requests_gost
        requests = requests_gost.requests
        
        # Тест GET
        response = requests.get(f'https://{url}/', verify=False, timeout=10)
        if response and hasattr(response, 'status_code'):
            print(f"  ✓ GET успешно! Статус: {response.status_code}")
            return True
        else:
            print(f"  ✗ Не удалось получить ответ")
            return False
    except Exception as e:
        print(f"  ✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("Тесты для gost_http wrapper библиотеки")
    print("=" * 60)
    print()
    
    results = []
    
    # Тест 1: Импорт модуля
    success, module = test_import_module()
    results.append(("Импорт модуля", success))
    print()
    
    if not success or not module:
        print("=" * 60)
        print("КРИТИЧЕСКАЯ ОШИБКА: Модуль не может быть импортирован")
        print("=" * 60)
        print("\nУбедитесь, что установлены зависимости:")
        print("  pip install requests pyOpenSSL cryptography")
        return 1
    
    # Собираем информацию о SSL для всех сайтов после успешных тестов
    # (будет заполнено после тестов)
    
    # Тест 2: gost_get() для всех сайтов
    for site in GOST_SITES:
        success = test_gost_get_function(site)
        results.append((f"gost_get() к {site}", success))
        # Собираем SSL информацию после успешного теста
        if success and site not in ssl_info:
            ssl_data = get_ssl_info(site)
            if ssl_data:
                ssl_info[site] = ssl_data
        print()
    
    # Тест 3: gost_session() для всех сайтов
    for site in GOST_SITES:
        success = test_gost_session(site)
        results.append((f"gost_session() к {site}", success))
        print()
    
    # Тест 4: GOSTHTTPClient для всех сайтов
    for site in GOST_SITES:
        success = test_gost_http_client(site)
        results.append((f"GOSTHTTPClient к {site}", success))
        print()
    
    # Тест 5: requests_gost для всех сайтов
    for site in GOST_SITES:
        success = test_requests_gost(site)
        results.append((f"requests_gost к {site}", success))
        print()
    
    # Тест 6: Тесты для сайтов со стандартными cipher suites
    for site in STANDARD_SITES:
        success = test_gost_get_function(site)
        results.append((f"gost_get() к {site} (стандартный)", success))
        # Собираем SSL информацию после успешного теста
        if success and site not in ssl_info:
            ssl_data = get_ssl_info(site)
            if ssl_data:
                ssl_info[site] = ssl_data
        print()
    
    # Итоги
    print("=" * 60)
    print("Итоги тестирования")
    print("=" * 60)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"Пройдено: {passed}/{total}")
    print(f"Провалено: {total - passed}/{total}")
    print()
    
    for test_name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {test_name}")
    
    # Вывод информации о методах шифрования
    if ssl_info:
        print()
        print("=" * 60)
        print("Информация о методах шифрования (Cipher Suites)")
        print("=" * 60)
        for url, info in ssl_info.items():
            print(f"\n{url}:")
            cipher_name = info.get('cipher_name', 'Unknown')
            cipher_version = info.get('cipher_version', 'Unknown')
            cipher_bits = info.get('cipher_bits', 'Unknown')
            is_gost = info.get('is_gost', False)
            
            print(f"  Протокол: {cipher_version}")
            print(f"  Cipher Suite: {cipher_name}")
            print(f"  Битность: {cipher_bits}")
            if is_gost:
                print(f"  Тип: GOST (российские криптографические алгоритмы)")
            else:
                print(f"  Тип: Стандартный")
    
    if passed == total:
        print("\n✓ Все тесты пройдены!")
        return 0
    else:
        print(f"\n✗ {total - passed} тест(ов) провалено")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())

