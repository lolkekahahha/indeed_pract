import pytest

class TestAdminAccess:
    def test_get_all_profiles_admin(self, admin_client):
        response = admin_client.get_all_profiles()

        assert response.status_code == 200
        data = response.json()

        profiles = data.get("profiles", data) if isinstance(data, dict) else data
        assert isinstance(profiles, (list, dict))

    def test_get_all_profiles_moderator_success(self, moderator_client):
        response = moderator_client.get_all_profiles()

        assert response.status_code == 200
        data = response.json()

        profiles = data.get("profiles", data) if isinstance(data, dict) else data
        assert isinstance(profiles, (list, dict)), "Ответ должен содержать список или объект профилей"

    def test_update_role_admin(self, admin_client):
        profiles_response = admin_client.get_all_profiles()
        users_data = profiles_response.json()
        users = users_data.get("profiles", users_data) if isinstance(users_data, dict) else users_data

        test_user = None
        for user in users:
            if isinstance(user, dict):
                role = user.get("role", {})
                if isinstance(role, dict) and role.get("name") == "user":
                    test_user = user
                    break
                elif user.get("role") == "user":
                    test_user = user
                    break

        if test_user is None:
            pytest.skip("Не найден пользователь с ролью 'user' для теста")

        account_id = test_user.get("id") or test_user.get("account_id")

        response = admin_client.update_role(account_id, "moderator")

        assert response.status_code in [200, 400]

    def test_update_role_moderator_forbidden(self, moderator_client):
        test_account_id = 1
        response = moderator_client.update_role(test_account_id, "admin")

        assert response.status_code in [403, 401, 405]

    def test_get_notes_by_role(self, admin_client):
        response = admin_client.session.get(
            f"{admin_client.base_url}/api/notes/",
            headers=admin_client._get_headers()
        )

        assert response.status_code == 200