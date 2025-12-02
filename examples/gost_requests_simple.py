#!/usr/bin/env python3
"""
Пример 1: Простое использование gost_http функций

Самый простой способ - использовать функции gost_get(), gost_post() и т.д.
"""

from gost_http import gost_get, gost_post, gost_put, gost_delete

def main():
    print("=" * 60)
    print("Пример 1: Простое использование gost_http")
    print("=" * 60)
    print()
    
    # GET запрос
    print("1. GET запрос к dss.uc-em.ru (только GOST)...")
    response = gost_get('https://dss.uc-em.ru/', timeout=10)
    if response:
        print(f"   ✓ Успешно! Status: {response.status_code}")
        print(f"   Размер ответа: {len(response.text)} символов")
    else:
        print("   ✗ Не удалось подключиться")
    print()
    
    # POST запрос (пример)
    print("2. POST запрос (пример)...")
    # response = gost_post('https://example-gost-api.ru/api', json={'key': 'value'})
    # if response:
    #     print(f"   ✓ Успешно! Status: {response.status_code}")
    print("   (Пример закомментирован - нужен реальный API endpoint)")
    print()
    
    # PUT запрос (пример)
    print("3. PUT запрос (пример)...")
    # response = gost_put('https://example-gost-api.ru/api/1', data={'key': 'value'})
    # if response:
    #     print(f"   ✓ Успешно! Status: {response.status_code}")
    print("   (Пример закомментирован - нужен реальный API endpoint)")
    print()
    
    # DELETE запрос (пример)
    print("4. DELETE запрос (пример)...")
    # response = gost_delete('https://example-gost-api.ru/api/1')
    # if response:
    #     print(f"   ✓ Успешно! Status: {response.status_code}")
    print("   (Пример закомментирован - нужен реальный API endpoint)")
    print()
    
    print("=" * 60)
    print("Пример завершен")
    print("=" * 60)

if __name__ == "__main__":
    main()

