#!/usr/bin/env python3
"""
Пример 3: Использование requests_gost (полная замена requests)

Самый простой способ миграции - просто заменить импорт:
    import requests  ->  from gost_http import requests_gost; requests = requests_gost.requests

Весь остальной код остается без изменений!
"""

# Вместо: import requests
from gost_http import requests_gost
requests = requests_gost.requests  # Получаем объект requests из модуля

def main():
    print("=" * 60)
    print("Пример 3: Использование requests_gost (полная замена requests)")
    print("=" * 60)
    print()
    
    print("Код выглядит точно так же, как с обычным requests!")
    print()
    
    # GET запрос - работает как обычно
    print("1. GET запрос...")
    response = requests.get('https://dss.uc-em.ru/', verify=False, timeout=10)
    if response:
        print(f"   ✓ Успешно! Status: {response.status_code}")
        print(f"   Размер ответа: {len(response.text)} символов")
    else:
        print("   ✗ Не удалось подключиться")
    print()
    
    # POST запрос - работает как обычно
    print("2. POST запрос (пример)...")
    # response = requests.post('https://example-gost-api.ru/api', json={'key': 'value'})
    # if response:
    #     print(f"   ✓ Успешно! Status: {response.status_code}")
    print("   (Пример закомментирован - нужен реальный API endpoint)")
    print()
    
    # PUT запрос - работает как обычно
    print("3. PUT запрос (пример)...")
    # response = requests.put('https://example-gost-api.ru/api/1', data={'key': 'value'})
    # if response:
    #     print(f"   ✓ Успешно! Status: {response.status_code}")
    print("   (Пример закомментирован - нужен реальный API endpoint)")
    print()
    
    # DELETE запрос - работает как обычно
    print("4. DELETE запрос (пример)...")
    # response = requests.delete('https://example-gost-api.ru/api/1')
    # if response:
    #     print(f"   ✓ Успешно! Status: {response.status_code}")
    print("   (Пример закомментирован - нужен реальный API endpoint)")
    print()
    
    print("=" * 60)
    print("Преимущества requests_gost:")
    print("  - Полная совместимость с requests API")
    print("  - Автоматическая поддержка GOST сайтов")
    print("  - Минимальные изменения в коде (только импорт)")
    print("=" * 60)

if __name__ == "__main__":
    main()

