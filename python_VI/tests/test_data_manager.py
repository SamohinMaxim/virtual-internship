import pytest
from data_manager import PerevalDataManager


class TestPerevalDataManager:
    @pytest.fixture
    def data_manager(self):
        return PerevalDataManager()

    def test_add_user(self, data_manager, mock_data_manager):
        # Мокаем выполнение запроса к БД
        mock_data_manager._get_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = (1,)
        mock_data_manager._get_connection.return_value.__enter__.return_value.commit.return_value = None

        user_id = data_manager.add_user(
            email="test@example.com",
            phone="+71234567890",
            fam="Иванов",
            name="Иван",
            otc="Иванович"
        )

        assert user_id == 1

    def test_add_coords(self, data_manager, mock_data_manager):
        mock_data_manager._get_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = (1,)
        mock_data_manager._get_connection.return_value.__enter__.return_value.commit.return_value = None

        coord_id = data_manager.add_coords(
            latitude=49.12345,
            longitude=86.54321,
            height=1500
        )

        assert coord_id == 1

    def test_submit_pereval_data_success(self, data_manager, mock_data_manager):
        test_data = {
            "user": {
                "email": "test@example.com",
                "phone": "+71234567890",
                "fam": "Иванов",
                "name": "Иван",
                "otc": "Иванович"
            },
            "coords": {
                "latitude": 49.12345,
                "longitude": 86.54321,
                "height": 1500
            },
            "level": {
                "winter": "1A",
                "summer": "1A",
                "autumn": "1A",
                "spring": "1A"
            },
            "beauty_title": "Перевал красоты",
            "title": "Главный перевал",
            "other_titles": "Вершина мира",
            "connect": "Путь к вершине",
            "images": [
                {
                    "img_path": "/path/to/image1.jpg",
                    "title": "Фото 1"
                }
            ]
        }

        # Настраиваем моки для всех зависимых методов
        mock_data_manager.add_user.return_value = 1
        mock_data_manager.add_coords.return_value = 2
        mock_data_manager.add_levels.return_value = 3
        mock_data_manager.add_pereval.return_value = 4
        mock_data_manager.add_image.return_value = 5
        mock_data_manager.link_pereval_image.return_value = None

        result = data_manager.submit_pereval_data(test_data)

        assert result["status"] == "success"
        assert result["pereval_id"] == 4

    def test_submit_pereval_data_error(self, data_manager, mock_data_manager):
        test_data = {}

        mock_data_manager.add_user.side_effect = Exception("DB Error")

        result = data_manager.submit_pereval_data(test_data)

        assert result["status"] == "error"
        assert "DB Error" in result["message"]

    def test_get_pereval_by_id(self, data_manager, mock_data_manager):
        expected_result = {
            "id": 1,
            "beauty_title": "Перевал красоты",
            "title": "Главный перевал"
        }
        mock_data_manager._get_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = expected_result

        result = data_manager.get_pereval_by_id(1)

        assert result == expected_result

    def test_update_pereval_if_new(self, data_manager, mock_data_manager):
        update_data = {"beauty_title": "Обновлённое название"}
        mock_data_manager._get_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = ("new",)
        mock_data_manager._get_connection.return_value.__enter__.return_value.commit.return_value = None

        result = data_manager.update_pereval_if_new(1, update_data)

        assert result["state"] == 1

    def test_get_perevals_by_user_email(self, data_manager, mock_data_manager):
        email = "test@example.com"
        expected_result = [{"id": 1, "title": "Главный перевал"}]
        mock_data_manager._get_connection.return_value.__enter__.return_value.cursor.return_value.fetchall.return_value = [expected_result[0]]

        result = data_manager.get_perevals_by_user_email(email)

        assert result == expected_result
