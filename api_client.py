import requests
from typing import Optional, Dict, Any
from requests.exceptions import RequestException, Timeout, ConnectionError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIError(Exception):

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class APIClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.timeout = timeout

    def _get_headers(self, with_auth: bool = True) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if with_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)

        try:
            response = self.session.request(method, url, **kwargs)
            logger.debug(f"{method} {url} -> {response.status_code}")
            return response
        except Timeout:
            logger.error(f"Timeout при запросе {method} {url}")
            raise APIError(f"Запрос превысил таймаут {self.timeout} секунд")
        except ConnectionError:
            logger.error(f"Ошибка подключения к {url}")
            raise APIError(f"Не удалось подключиться к {self.base_url}")
        except RequestException as e:
            logger.error(f"Ошибка запроса: {e}")
            raise APIError(f"Ошибка при выполнении запроса: {str(e)}")

    def login(self, username: str, password: str) -> requests.Response:
        url = f"{self.base_url}/api/auth/login"
        payload = {"username": username, "password": password}

        response = self._make_request("POST", url, json=payload, headers={"Content-Type": "application/json"})

        if response.status_code == 200:
            try:
                data = response.json()
                self.token = data.get("access_token")
                if not self.token:
                    raise APIError("Токен отсутствует в ответе сервера", status_code=200, response_data=data)
                logger.info(f"Успешный вход пользователя: {username}")
            except ValueError as e:
                raise APIError(f"Невалидный JSON ответ: {e}", status_code=response.status_code)

        return response

    def register(self, username: str, password: str, email: str) -> requests.Response:
        url = f"{self.base_url}/api/auth/register"
        payload = {"username": username, "password": password, "email": email}
        return self._make_request("POST", url, json=payload, headers={"Content-Type": "application/json"})

    def get_my_profile(self) -> requests.Response:
        url = f"{self.base_url}/api/profiles/me"
        return self._make_request("GET", url, headers=self._get_headers())

    def create_my_profile(self, data: Dict[str, Any]) -> requests.Response:
        url = f"{self.base_url}/api/profiles/"
        return self._make_request("POST", url, json=data, headers=self._get_headers())

    def update_my_profile(self, data: Dict[str, Any]) -> requests.Response:
        url = f"{self.base_url}/api/profiles/me"
        return self._make_request("PUT", url, json=data, headers=self._get_headers())

    def get_all_profiles(self) -> requests.Response:
        url = f"{self.base_url}/api/profiles/"
        return self._make_request("GET", url, headers=self._get_headers())

    def update_role(self, account_id: int, role_name: str) -> requests.Response:
        url = f"{self.base_url}/api/profiles/{account_id}/role"
        params = {"role_name": role_name}
        return self._make_request("PUT", url, params=params, headers=self._get_headers())

    def logout(self):
        self.token = None
        logger.info("Выполнен выход из системы")