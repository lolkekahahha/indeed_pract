import pytest
from api_client import APIClient
from config import Config


@pytest.fixture(scope="session")
def api_client():
    client = APIClient(Config.BASE_URL)
    yield client
    client.logout()


@pytest.fixture(scope="function")
def authenticated_client():
    client = APIClient(Config.BASE_URL)

    login_resp = client.login(Config.TEST_USER["login"], Config.TEST_USER["password"])
    if login_resp.status_code != 200:
        client.register(
            username=Config.TEST_USER["login"],
            password=Config.TEST_USER["password"],
            email=Config.TEST_USER["email"]
        )
        client.login(Config.TEST_USER["login"], Config.TEST_USER["password"])

    profile_resp = client.get_my_profile()
    if profile_resp.status_code == 404:
        create_resp = client.create_my_profile({
            "name": "AutoTest",
            "surname": "QA",
            "about": "Fixture-created"
        })
        assert create_resp.status_code in [200, 201], f"Не удалось создать профиль: {create_resp.text}"

    yield client
    client.logout()

@pytest.fixture(scope="function")
def admin_client():
    client = APIClient(Config.BASE_URL)
    client.login(Config.ADMIN["login"], Config.ADMIN["password"])
    yield client
    client.logout()


@pytest.fixture(scope="function")
def moderator_client():
    client = APIClient(Config.BASE_URL)
    client.login(Config.MODERATOR["login"], Config.MODERATOR["password"])
    yield client
    client.logout()