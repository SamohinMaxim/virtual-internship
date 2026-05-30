import json
import pytest


class TestPerevalAPI:
    def test_submit_and_retrieve_pereval(self, client, mock_data_manager):
        """Тест: добавляем перевал и сразу получаем его по ID"""
        post_data = {
            "user": {
                "email": "test_api@example.com",
                "phone": "+71234567890",
                "fam": "Петров",
                "name": "Пётр",
                "otc": "Петрович"
            },
            "coords": {
                "latitude": 50.12345,
                "longitude": 87.54321,
                "height": 2000
            },
            "level": {
                "winter": "2A",
                "summer": "2A",
                "autumn": "2A",
                "spring": "2A"
            },
            "beauty_title": "Красивый перевал",
            "title": "Восточный перевал",
            "other_titles": "Горный путь",
            "connect": "Основной маршрут"
        }

        # Мокаем метод submit_pereval_data
        mock_data_manager.submit_pereval_data.return_value = {
            "status": "success",
            "message": "Заявка успешно добавлена",
            "pereval_id": 999
        }

        response = client.post(
            '/submitData',
            data=json.dumps(post_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data["status"] == "success"
        pereval_id = response_data["pereval_id"]

        # Теперь получаем перевал по ID
        expected_get_result = {
            "id": pereval_id,
            "beauty_title": post_data["beauty_title"],
            "title": post_data["title"],
            "email": post_data["user"]["email"],
            "latitude": post_data["coords"]["latitude"],
            "longitude": post_data["coords"]["longitude"],
            "height": post_data["coords"]["height"]
        }
        mock_data_manager.get_pereval_by_id.return_value = expected_get_result

        get_response = client.get(f'/perevals/{pereval_id}')
        assert get_response.status_code == 200
        get_data = json.loads(get_response.data)

        # Проверяем ключевые поля
        assert get_data["id"] == pereval_id
        assert get_data["title"] == post_data["title"]
        assert get_data["email"] == post_data["user"]["email"]
        assert get_data["latitude"] == post_data["coords"]["latitude"]
        assert get_data["longitude"] == post_data["coords"]["longitude"]
        assert get_data["height"] == post_data["coords"]["height"]
        assert get_data["beauty_title"] == post_data["beauty_title"]

    def test_retrieve_nonexistent_pereval(self, client, mock_data_manager):
        """Тест: попытка получить перевал с несуществующим ID"""
        mock_data_manager.get_pereval_by_id.return_value = None

        response = client.get('/perevals/9999')
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data["status"] == "error"
        assert "Pereval not found" in response_data["message"]

    def test_update_pereval(self, client, mock_data_manager):
        """Тест: обновление перевала"""
        # Сначала имитируем успешное добавление перевала
        mock_data_manager.submit_pereval_data.return_value = {
            "status": "success",
            "message": "Заявка успешно добавлена",
            "pereval_id": 999
        }

        post_data = {
            "user": {
                "email": "test_update@example.com",
                "phone": "+71234567890",
                "fam": "Сидоров",
                "name": "Сергей",
                "otc": "Сергеевич"
            },
            "coords": {
                "latitude": 51.12345,
                "longitude": 88.54321,
                "height": 2100
            },
            "level": {
                "winter": "2B",
                "summer": "2B",
                "autumn": "2B",
                "spring": "2B"
            },
            "beauty_title": "Перевал для обновления",
            "title": "Обновляемый перевал",
            "other_titles": "Тестовый маршрут",
            "connect": "Путь для теста"
        }

        response = client.post(
            '/submitData',
            data=json.dumps(post_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        pereval_id = json.loads(response.data)["pereval_id"]

        # Готовим данные для обновления
        update_data = {
            "beauty_title": "Обновлённый заголовок",
            "coords": {
                "latitude": 52.12345,
                "longitude": 89.54321,
                "height": 2200
            }
        }

        # Мокаем метод update_pereval_if_new
        mock_data_manager.update_pereval_if_new.return_value = {"state": 1, "message": "Successfully updated"}

        patch_response = client.patch(
            f'/perevals/{pereval_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert patch_response.status_code == 200
        patch_data = json.loads(patch_response.data)
        assert patch_data["state"] == 1

    def test_get_user_perevals(self, client, mock_data_manager):
        """Тест: получение перевалов пользователя по email"""
        email = "test_user@example.com"
        expected_perevals = [
            {
                "id": 1,
                "title": "Первый перевал",
                "beauty_title": "Красивый перевал 1"
            },
            {
                "id": 2,
                "title": "Второй перевал",
                "beauty_title": "Красивый перевал 2"
            }
        ]
        mock_data_manager.get_perevals_by_user_email.return_value = expected_perevals

        response = client.get(f'/user?user__email={email}')
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["status"] == "success"
        assert response_data["data"] == expected_perevals

    def test_submit_data_missing_fields(self, client):
        """Тест: отправка данных с отсутствующими обязательными полями"""
        incomplete_data = {
            "user": {
                "email": "test@example.com"
            },
            # Отсутствует coords, level и title
        }

        response = client.post(
            '/submitData',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["status"] == "error"
        assert "Missing required fields" in response_data["message"]
        assert "title" in response_data["message"]
        assert "coords" in response_data["message"]
        assert "level" in response_data["message"]

    def test_submit_data_invalid_content_type(self, client):
        """Тест: отправка данных без заголовка Content-Type: application/json"""
        response = client.post(
            '/submitData',
            data="not json data"
            # content_type не указан, будет использован по умолчанию
        )
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data["status"] == "error"
        assert "Content-Type must be application/json" in response_data["message"]
