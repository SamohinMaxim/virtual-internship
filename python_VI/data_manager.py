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

    def get_pereval_by_id(self, pereval_id: int) -> Optional[Dict]:
        """Получить перевал по ID вместе со всей связанной информацией."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT
                        pa.id,
                        pa.beauty_title,
                        pa.title,
                        pa.other_titles,
                        pa.connect,
                        pa.add_time,
                        pa.status,
                        u.email,
                        u.phone,
                        u.fam,
                        u.name,
                        u.otc,
                        c.latitude,
                        c.longitude,
                        c.height,
                        l.winter,
                        l.summer,
                        l.autumn,
                        l.spring,
                        ARRAY_AGG(json_build_object('img_path', i.img_path, 'title', i.title)) FILTER (WHERE i.id IS NOT NULL) AS images
                    FROM pereval_added pa
                    LEFT JOIN users u ON pa.user_id = u.id
                    LEFT JOIN coords c ON pa.coord_id = c.id
                    LEFT JOIN levels l ON pa.level_id = l.id
                    LEFT JOIN pereval_images pi ON pa.id = pi.pereval_id
                    LEFT JOIN images i ON pi.image_id = i.id
                    WHERE pa.id = %s
                    GROUP BY pa.id, u.id, c.id, l.id
                """, (pereval_id,))
                row = cursor.fetchone()
                if row is None:
                    return None
                return dict(row)

    def update_pereval_if_new(self, pereval_id: int, data: Dict) -> Dict[str, any]:
        """
        Редактировать перевал, если его статус 'new'.
        Возвращает словарь с полями state и message.
        """
        with self._get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    # Проверяем статус
                    cursor.execute(
                        "SELECT status FROM pereval_added WHERE id = %s",
                        (pereval_id,)
                    )
                    row = cursor.fetchone()
                    if not row:
                        return {'state': 0, 'message': 'Pereval not found'}
                    if row[0] != 'new':
                        return {'state': 0, 'message': 'Cannot edit pereval: status is not "new"'}

                    # Обновляем координаты
                    if 'coords' in data:
                        cursor.execute(
                            "UPDATE coords SET latitude = %s, longitude = %s, height = %s WHERE id = (SELECT coord_id FROM pereval_added WHERE id = %s)",
                            (data['coords'].get('latitude'),
                             data['coords'].get('longitude'),
                             data['coords'].get('height'),
                             pereval_id)
                        )

                    # Обновляем уровень сложности
                    if 'level' in data:
                        cursor.execute(
                            "UPDATE levels SET winter = %s, summer = %s, autumn = %s, spring = %s WHERE id = (SELECT level_id FROM pereval_added WHERE id = %s)",
                            (data['level'].get('winter'),
                             data['level'].get('summer'),
                             data['level'].get('autumn'),
                             data['level'].get('spring'),
                             pereval_id)
                        )

                    # Обновляем основную запись перевала
                    cursor.execute(
                        """UPDATE pereval_added
                           SET beauty_title = %s, title = %s, other_titles = %s, connect = %s, add_time = %s
                           WHERE id = %s""",
                        (data.get('beautyTitle'),
                         data.get('title'),
                         data.get('other_titles'),
                         data.get('connect'),
                         data.get('add_time'),
                         pereval_id)
                    )

                    # Обрабатываем изображения: удаляем старые, добавляем новые
                    if 'images' in data:
                        # Удаляем старые связи
                        cursor.execute(
                            "DELETE FROM pereval_images WHERE pereval_id = %s",
                            (pereval_id,)
                        )
                        for image_data in data['images']:
                            cursor.execute(
                                "INSERT INTO images (img_path, title) VALUES (%s, %s) RETURNING id",
                                (image_data['img_path'], image_data.get('title'))
                            )
                            image_id = cursor.fetchone()[0]
                            cursor.execute(
                                "INSERT INTO pereval_images (pereval_id, image_id) VALUES (%s, %s)",
                                (pereval_id, image_id)
                            )

                conn.commit()
                return {'state': 1, 'message': 'Successfully updated'}
            except Exception as e:
                conn.rollback()
                return {'state': 0, 'message': str(e)}

    def get_perevals_by_user_email(self, email: str) -> List[Dict]:
        """Получить все перевалы пользователя по email."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT
                        pa.id,
                        pa.beauty_title,
                        pa.title,
                        pa.other_titles,
                        pa.connect,
                        pa.add_time,
                        pa.status,
                        u.email,
                        c.latitude,
                        c.longitude,
                        c.height,
                        l.winter,
                        l.summer,
                        l.autumn,
                        l.spring,
                        ARRAY_AGG(json_build_object('img_path', i.img_path, 'title', i.title)) FILTER (WHERE i.id IS NOT NULL) AS images
                    FROM pereval_added pa
                    JOIN users u ON pa.user_id = u.id
                    JOIN coords c ON pa.coord_id = c.id
                    JOIN levels l ON pa.level_id = l.id
                    LEFT JOIN pereval_images pi ON pa.id = pi.pereval_id
                    LEFT JOIN images i ON pi.image_id = i.id
                    WHERE u.email = %s
                    GROUP BY pa.id, u.id, c.id, l.id
                """, (email,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
