from config import Config
import pytest


class TestAuthentication:

    def test_login_success_admin(self, api_client):
        response = api_client.login(
            username=Config.ADMIN["login"],
            password=Config.ADMIN["password"]
        )

        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}. Ответ: {response.text}"

        data = response.json()
        assert "access_token" in data, "Ответ не содержит access_token"
        assert isinstance(data["access_token"], str), "access_token должен быть строкой"
        assert len(data["access_token"]) > 0, "access_token не может быть пустым"
        assert api_client.token is not None, "Токен не сохранен в клиенте"

    def test_login_success_moderator(self, api_client):
        response = api_client.login(
            username=Config.MODERATOR["login"],
            password=Config.MODERATOR["password"]
        )

        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
        data = response.json()
        assert "access_token" in data, "Ответ не содержит access_token"

    def test_login_wrong_password(self, api_client):
        response = api_client.login(
            username=Config.ADMIN["login"],
            password="WrongPassword123"
        )

        assert response.status_code in [401, 403], \
            f"Ожидался 401 или 403, получен {response.status_code}. Ответ: {response.text}"

        try:
            error_data = response.json()
            if response.status_code == 401:
                assert "error" in error_data or "detail" in error_data or "message" in error_data, \
                    "Ответ ошибки должен содержать описание проблемы"
        except ValueError:
            assert response.text, "Ответ ошибки не должен быть пустым"

    def test_login_nonexistent_user(self, api_client):
        response = api_client.login(
            username="nonexistent_user_xyz_" + pytest.unique_id if hasattr(pytest,
                                                                           'unique_id') else "nonexistent_user_xyz",
            password="AnyPassword123"
        )

        assert response.status_code in [401, 404], \
            f"Ожидался 401 или 404, получен {response.status_code}. Ответ: {response.text}"

    def test_request_without_token(self, api_client):
        api_client.logout()
        response = api_client.get_my_profile()

        assert response.status_code in [401, 403], \
            f"Ожидался 401 или 403, получен {response.status_code}. Ответ: {response.text}"

        try:
            error_data = response.json()
            error_message = str(error_data)
            assert any(keyword in error_message.lower() for keyword in ["unauthorized", "token", "auth"]), \
                "Сообщение об ошибке должно указывать на проблему авторизации"
        except ValueError:
            pass

    def test_token_in_authorization_header(self, api_client):
        response = api_client.login(
            username=Config.ADMIN["login"],
            password=Config.ADMIN["password"]
        )
        assert response.status_code == 200, "Не удалось получить токен"

        headers = api_client._get_headers(with_auth=True)
        assert "Authorization" in headers, "Отсутствует Authorization header"
        assert headers["Authorization"].startswith("Bearer "), "Authorization header должен начинаться с 'Bearer '"

        token = headers["Authorization"].replace("Bearer ", "")
        assert len(token) > 0, "Токен не может быть пустым"
        assert Config.ADMIN["password"] not in headers["Authorization"], \
            "Пароль не должен быть в Authorization header"