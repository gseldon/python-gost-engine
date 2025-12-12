#!/usr/bin/env python3
"""
Пример: POST запросы с form data через gost_http

Демонстрирует использование POST запросов с application/x-www-form-urlencoded данными
для работы с GOST сайтами.
"""

from gost_http import GOSTHTTPClient, gost_post
import base64

def main():
    print("=" * 60)
    print("Пример: POST запросы с form data")
    print("=" * 60)
    print()
    
    # Пример 1: POST запрос через GOSTHTTPClient
    print("1. POST запрос через GOSTHTTPClient...")
    client = GOSTHTTPClient(verify=False, timeout=30.0)
    
    # Подготовка form data
    form_data = {
        'grant_type': 'password',
        'username': 'user@example.com',
        'password': 'your_password',
        'resource': 'urn:cryptopro:dss:signserver:signserver'
    }
    
    # Подготовка заголовков
    client_id = "your_client_id"
    client_secret = "your_client_secret"
    credentials = f"{client_id}:{client_secret}"
    auth_header = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {auth_header}'
    }
    
    # Отправка POST запроса
    # response = client.post('https://example-gost-api.ru/oauth/token', 
    #                        data=form_data, headers=headers)
    # if response:
    #     print(f"   ✓ Успешно! Status: {response.status_code}")
    #     if response.status_code == 200:
    #         json_data = response.json()
    #         if 'access_token' in json_data:
    #             print(f"   ✓ Получен access_token")
    # else:
    #     print("   ✗ Не удалось отправить запрос")
    print("   (Пример закомментирован - замените URL и credentials на реальные)")
    print()
    
    # Пример 2: POST запрос через функцию gost_post()
    print("2. POST запрос через функцию gost_post()...")
    # response = gost_post(
    #     'https://example-gost-api.ru/oauth/token',
    #     data=form_data,
    #     headers=headers,
    #     verify=False,
    #     timeout=30.0
    # )
    # if response:
    #     print(f"   ✓ Успешно! Status: {response.status_code}")
    print("   (Пример закомментирован - замените URL и credentials на реальные)")
    print()
    
    # Пример 3: POST запрос с JSON данными
    print("3. POST запрос с JSON данными...")
    json_data = {
        'key': 'value',
        'number': 123
    }
    # response = client.post(
    #     'https://example-gost-api.ru/api/endpoint',
    #     json=json_data,
    #     headers={'Content-Type': 'application/json'}
    # )
    # if response:
    #     print(f"   ✓ Успешно! Status: {response.status_code}")
    print("   (Пример закомментирован - замените URL на реальный)")
    print()
    
    print("=" * 60)
    print("Важные замечания:")
    print("=" * 60)
    print("1. POST запросы автоматически используют curl fallback при ошибках SSL")
    print("2. Form data (dict) автоматически кодируется в application/x-www-form-urlencoded")
    print("3. JSON данные передаются через параметр json (не data)")
    print("4. Все методы поддерживают стандартные параметры requests (headers, timeout, и т.д.)")
    print("=" * 60)

if __name__ == "__main__":
    main()

