"""
requests_gost - полная замена requests с поддержкой GOST

Использование:
    from gost_http import requests_gost
    import requests_gost as requests
    
    # Теперь все методы requests автоматически поддерживают GOST
    response = requests.get('https://dss.uc-em.ru/')
    response = requests.post('https://dss.uc-em.ru/api', json={'key': 'value'})
"""

from gost_http.gost_http_client import GOSTHTTPClient
import requests as _original_requests

class RequestsGOST:
    """
    Полная замена requests с поддержкой GOST
    
    API полностью совместим с requests, но автоматически использует
    GOST поддержку для сайтов только с GOST cipher suites.
    """
    
    def __init__(self):
        self._client = GOSTHTTPClient()
        # Сохраняем оригинальные классы и функции для совместимости
        self.Session = _original_requests.Session
        self.Response = _original_requests.Response
        self.exceptions = _original_requests.exceptions
        self.codes = _original_requests.codes
        self.status_codes = _original_requests.status_codes
    
    def get(self, url, **kwargs):
        """GET запрос с поддержкой GOST"""
        return self._client.get(url, **kwargs)
    
    def post(self, url, **kwargs):
        """POST запрос с поддержкой GOST"""
        return self._client.post(url, **kwargs)
    
    def put(self, url, **kwargs):
        """PUT запрос с поддержкой GOST"""
        return self._client.put(url, **kwargs)
    
    def delete(self, url, **kwargs):
        """DELETE запрос с поддержкой GOST"""
        return self._client.delete(url, **kwargs)
    
    def patch(self, url, **kwargs):
        """PATCH запрос с поддержкой GOST"""
        return self._client.patch(url, **kwargs)
    
    def head(self, url, **kwargs):
        """HEAD запрос с поддержкой GOST"""
        return self._client.head(url, **kwargs)
    
    def options(self, url, **kwargs):
        """OPTIONS запрос с поддержкой GOST"""
        return self._client.options(url, **kwargs)
    
    def request(self, method, url, **kwargs):
        """Универсальный метод request с поддержкой GOST"""
        return self._client._request(method, url, **kwargs)

# Создаем экземпляр для удобного использования
requests = RequestsGOST()

