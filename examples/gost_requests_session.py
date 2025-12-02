#!/usr/bin/env python3
"""
Пример 2: Использование сессий

Рекомендуется для множественных запросов к одному или нескольким сайтам.
"""

from gost_http import gost_session

def main():
    print("=" * 60)
    print("Пример 2: Использование сессий")
    print("=" * 60)
    print()
    
    # Создаем сессию
    session = gost_session(verify=False, timeout=10)
    
    # Множественные запросы через одну сессию
    sites = [
        'https://dss.uc-em.ru/',
        'https://cryptopro.ru/'
    ]
    
    for i, url in enumerate(sites, 1):
        print(f"{i}. Запрос к {url}...")
        response = session.get(url)
        if response:
            print(f"   ✓ Успешно! Status: {response.status_code}")
            print(f"   Размер ответа: {len(response.text)} символов")
        else:
            print("   ✗ Не удалось подключиться")
        print()
    
    # POST запрос через сессию (пример)
    print("3. POST запрос через сессию (пример)...")
    # response = session.post('https://example-gost-api.ru/api', json={'data': 'value'})
    # if response:
    #     print(f"   ✓ Успешно! Status: {response.status_code}")
    print("   (Пример закомментирован - нужен реальный API endpoint)")
    print()
    
    print("=" * 60)
    print("Пример завершен")
    print("=" * 60)

if __name__ == "__main__":
    main()

