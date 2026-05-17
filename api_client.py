import requests
from typing import Optional, Dict, Any


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.token: Optional[str] = None

    def _get_headers(self, with_auth: bool = True) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if with_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, username: str, password: str) -> requests.Response:
        url = f"{self.base_url}/api/auth/login"
        payload = {"username": username, "password": password}
        response = self.session.post(url, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
        return response

    def register(self, username: str, password: str, email: str) -> requests.Response:
        url = f"{self.base_url}/api/auth/register"
        payload = {"username": username, "password": password, "email": email}
        return self.session.post(url, json=payload, headers={"Content-Type": "application/json"})

    def get_my_profile(self) -> requests.Response:
        url = f"{self.base_url}/api/profiles/me"
        return self.session.get(url, headers=self._get_headers())

    def create_my_profile(self, data: Dict[str, Any]) -> requests.Response:
        url = f"{self.base_url}/api/profiles/"
        return self.session.post(url, json=data, headers=self._get_headers())

    def update_my_profile(self, data: Dict[str, Any]) -> requests.Response:
        url = f"{self.base_url}/api/profiles/me"
        return self.session.put(url, json=data, headers=self._get_headers())

    def get_all_profiles(self) -> requests.Response:
        url = f"{self.base_url}/api/profiles/"
        return self.session.get(url, headers=self._get_headers())

    def update_role(self, account_id: int, role_name: str) -> requests.Response:
        url = f"{self.base_url}/api/profiles/{account_id}/role"
        params = {"role_name": role_name}
        return self.session.put(url, params=params, headers=self._get_headers())

    def logout(self):
        self.token = None