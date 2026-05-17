from config import Config

class TestAuthentication:
    def test_login_success_admin(self, api_client):
        response = api_client.login(
            username=Config.ADMIN["login"],
            password=Config.ADMIN["password"]
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert api_client.token is not None

    def test_login_success_moderator(self, api_client):
        response = api_client.login(
            username=Config.MODERATOR["login"],
            password=Config.MODERATOR["password"]
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_wrong_password(self, api_client):
        response = api_client.login(
            username=Config.ADMIN["login"],
            password="WrongPassword123"
        )

        assert response.status_code in [401, 403]

    def test_login_nonexistent_user(self, api_client):
        response = api_client.login(
            username="nonexistent_user_xyz",
            password="AnyPassword123"
        )

        assert response.status_code in [401, 404]

    def test_request_without_token(self, api_client):
        api_client.logout()
        response = api_client.get_my_profile()

        assert response.status_code in [401, 403]

    def test_token_in_authorization_header(self, api_client):
        api_client.login(
            username=Config.ADMIN["login"],
            password=Config.ADMIN["password"]
        )

        headers = api_client._get_headers(with_auth=True)
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")
        assert Config.ADMIN["password"] not in headers["Authorization"]