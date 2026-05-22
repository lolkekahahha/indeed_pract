import pytest


class TestAdminAccess:

    def test_get_all_profiles_admin(self, admin_client):
        response = admin_client.get_all_profiles()

        assert response.status_code == 200, \
            f"Ожидался 200, получен {response.status_code}. Ответ: {response.text}"

        data = response.json()
        profiles = data.get("profiles", data) if isinstance(data, dict) else data

        assert isinstance(profiles, (list, dict)), \
            f"Ответ должен содержать список или объект профилей, получено: {type(profiles)}"

        # Проверка структуры хотя бы одного профиля
        if isinstance(profiles, list) and len(profiles) > 0:
            first_profile = profiles[0]
            assert isinstance(first_profile, dict), "Каждый профиль должен быть объектом"
            # Проверка наличия идентификатора
            assert any(key in first_profile for key in ["id", "account_id", "user_id"]), \
                "Профиль должен содержать идентификатор"

    def test_get_all_profiles_moderator_success(self, moderator_client):
        response = moderator_client.get_all_profiles()

        assert response.status_code == 200, \
            f"Ожидался 200, получен {response.status_code}. Ответ: {response.text}"

        data = response.json()
        profiles = data.get("profiles", data) if isinstance(data, dict) else data
        assert isinstance(profiles, (list, dict)), \
            f"Ответ должен содержать список или объект профилей, получено: {type(profiles)}"

    def test_update_role_admin(self, admin_client):
        profiles_response = admin_client.get_all_profiles()
        assert profiles_response.status_code == 200, "Не удалось получить список профилей"

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
        assert account_id, f"Не удалось получить ID пользователя: {test_user}"

        response = admin_client.update_role(account_id, "moderator")

        assert response.status_code in [200, 400], \
            f"Ожидался 200 или 400, получен {response.status_code}. Ответ: {response.text}"

        if response.status_code == 200:
            verify_response = admin_client.get_all_profiles()
            assert verify_response.status_code == 200
            updated_users = verify_response.json().get("profiles", verify_response.json())

            updated_user = None
            for user in updated_users:
                if isinstance(user, dict) and (user.get("id") == account_id or user.get("account_id") == account_id):
                    updated_user = user
                    break

            if updated_user:
                role_value = updated_user.get("role", {})
                if isinstance(role_value, dict):
                    assert role_value.get("name") == "moderator", "Роль не обновилась на moderator"
                else:
                    assert role_value == "moderator", "Роль не обновилась на moderator"

    def test_update_role_moderator_forbidden(self, moderator_client):
        test_account_id = 1

        response = moderator_client.update_role(test_account_id, "admin")

        assert response.status_code in [403, 401, 405], \
            f"Ожидался 403, 401 или 405, получен {response.status_code}. Ответ: {response.text}"

        try:
            error_data = response.json()
            error_text = str(error_data).lower()

            keywords = ["forbidden", "permission", "denied", "unauthorized", "access", "error", "role"]

            if len(error_text) > 0:
                print(f"\n[INFO] Текст ошибки: {error_text}")

                if not any(keyword in error_text for keyword in keywords):
                    print(f"[WARNING] Сообщение об ошибке не содержит ожидаемых ключевых слов")
        except ValueError:
            assert response.text, "Ответ ошибки не должен быть пустым"
            print(f"[INFO] Ответ не в JSON формате: {response.text}")

    def test_get_notes_by_role(self, admin_client):
        response = admin_client.session.get(
            f"{admin_client.base_url}/api/notes/",
            headers=admin_client._get_headers()
        )

        assert response.status_code == 200, \
            f"Ожидался 200, получен {response.status_code}. Ответ: {response.text}"

        try:
            data = response.json()
            assert isinstance(data, (list, dict)), "Ответ должен быть списком или объектом"
        except ValueError as e:
            pytest.fail(f"Ответ не является валидным JSON: {e}")