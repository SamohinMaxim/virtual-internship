import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Загружаем переменные окружения при импорте модуля
load_dotenv()

class PerevalDataManager:
    def __init__(self):
        """Инициализация подключения к БД с использованием переменных окружения"""
        self.connection_params = {
            'host': os.getenv('FSTR_DB_HOST', 'localhost'),
            'port': os.getenv('FSTR_DB_PORT', '5432'),
            'database': 'pereval',
            'user': os.getenv('FSTR_DB_LOGIN', 'postgres'),
            'password': os.getenv('FSTR_DB_PASS', '')
        }

    def _get_connection(self):
        """Создание соединения с БД"""
        return psycopg2.connect(**self.connection_params)

    def add_user(self, email: str, phone: str = None, fam: str = None,
                  name: str = None, otc: str = None) -> int:
        """Добавление пользователя в таблицу users. Возвращает ID созданного пользователя."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (email, phone, fam, name, otc) "
                    "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (email, phone, fam, name, otc)
                )
                user_id = cursor.fetchone()[0]
                conn.commit()
                return user_id

    def add_coords(self, latitude: float, longitude: float, height: int = None) -> int:
        """Добавление координат в таблицу coords. Возвращает ID созданных координат."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO coords (latitude, longitude, height) "
                    "VALUES (%s, %s, %s) RETURNING id",
                    (latitude, longitude, height)
                )
                coord_id = cursor.fetchone()[0]
                conn.commit()
                return coord_id

    def add_levels(self, winter: str = None, summer: str = None,
                  autumn: str = None, spring: str = None) -> int:
        """Добавление уровня сложности в таблицу levels. Возвращает ID уровня."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO levels (winter, summer, autumn, spring) "
                    "VALUES (%s, %s, %s, %s) RETURNING id",
                    (winter, summer, autumn, spring)
                )
                level_id = cursor.fetchone()[0]
                conn.commit()
                return level_id

    def add_pereval(self,
                    beauty_title: str = None,
                    title: str = None,
            other_titles: str = None,
            connect: str = None,
            add_time: str = None,
            user_id: int = None,
            coord_id: int = None,
            level_id: int = None) -> int:
        """
        Добавление перевала в таблицу pereval_added.
        Статус автоматически устанавливается как 'new'.
        Возвращает ID созданного перевала.
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO pereval_added "
                    "(beauty_title, title, other_titles, connect, add_time, user_id, coord_id, level_id, status) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'new') RETURNING id",
                    (beauty_title, title, other_titles, connect, add_time, user_id, coord_id, level_id)
                )
                pereval_id = cursor.fetchone()[0]
                conn.commit()
                return pereval_id

    def add_image(self, img_path: str, title: str = None) -> int:
        """Добавление изображения в таблицу images. Возвращает ID изображения."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO images (img_path, title) "
                    "VALUES (%s, %s) RETURNING id",
                    (img_path, title)
                )
                image_id = cursor.fetchone()[0]
                conn.commit()
                return image_id

    def link_pereval_image(self, pereval_id: int, image_id: int) -> None:
        """Связывание перевала с изображением в таблице pereval_images."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO pereval_images (pereval_id, image_id) "
                    "VALUES (%s, %s)",
                    (pereval_id, image_id)
                )
                conn.commit()

    def submit_pereval_data(self, data: Dict) -> Dict[str, any]:
        """
        Основной метод для обработки POST submitData.
        Принимает словарь с данными и последовательно создаёт все сущности.
        Возвращает словарь с ID созданных записей и статусом операции.
        """
        try:
            # 1. Добавляем пользователя
            user_id = self.add_user(
                email=data['user']['email'],
                phone=data['user'].get('phone'),
                fam=data['user'].get('fam'),
                name=data['user'].get('name'),
                otc=data['user'].get('otc')
            )

            # 2. Добавляем координаты
            coord_id = self.add_coords(
                latitude=data['coords']['latitude'],
                longitude=data['coords']['longitude'],
                height=data['coords'].get('height')
            )

            # 3. Добавляем уровень сложности
            level_id = self.add_levels(
                winter=data['level'].get('winter'),
                summer=data['level'].get('summer'),
                autumn=data['level'].get('autumn'),
                spring=data['level'].get('spring')
            )

            # 4. Добавляем перевал
            pereval_id = self.add_pereval(
                beauty_title=data.get('beautyTitle'),
                title=data['title'],
                other_titles=data.get('other_titles'),
                connect=data.get('connect'),
                add_time=data.get('add_time'),
                user_id=user_id,
                coord_id=coord_id,
                level_id=level_id
            )

            # 5. Добавляем изображения и связываем с перевалом
            image_ids = []
            for image_data in data.get('images', []):
                image_id = self.add_image(
                    img_path=image_data['img_path'],
                    title=image_data.get('title')
                )
                self.link_pereval_image(pereval_id, image_id)
                image_ids.append(image_id)

            return {
                'status': 'success',
                'pereval_id': pereval_id,
                'user_id': user_id,
                'coord_id': coord_id,
                'level_id': level_id,
                'image_ids': image_ids
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
