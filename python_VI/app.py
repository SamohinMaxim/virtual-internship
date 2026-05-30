from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(app, version='1.0', title='Pereval API',
           description='API для управления данными о перевалах')

# Модель данных для валидации и отображения в Swagger
user_model = api.model('User', {
    'email': fields.String(required=True, description='Email пользователя'),
    'phone': fields.String(description='Телефон пользователя'),
    'fam': fields.String(description='Фамилия'),
    'name': fields.String(description='Имя'),
    'otc': fields.String(description='Отчество')
})

coords_model = api.model('Coords', {
    'latitude': fields.Float(description='Широта'),
    'longitude': fields.Float(description='Долгота'),
    'height': fields.Integer(description='Высота')
})

level_model = api.model('Level', {
    'winter': fields.String(description='Уровень сложности зимой'),
    'summer': fields.String(description='Уровень сложности летом'),
    'autumn': fields.String(description='Уровень сложности осенью'),
    'spring': fields.String(description='Уровень сложности весной')
})

image_model = api.model('Image', {
    'img_path': fields.String(description='Путь к изображению'),
    'title': fields.String(description='Название изображения')
})

pereval_model = api.model('Pereval', {
    'user': fields.Nested(user_model),
    'coords': fields.Nested(coords_model),
    'level': fields.Nested(level_model),
    'beauty_title': fields.String(description='Красочное название'),
    'title': fields.String(description='Основное название'),
    'other_titles': fields.String(description='Другие названия'),
    'connect': fields.String(description='Описание маршрута'),
    'images': fields.List(fields.Nested(image_model))
})

@api.route('/submitData')
class SubmitData(Resource):
    @api.expect(pereval_model)
    @api.response(201, 'Заявка успешно добавлена')
    @api.response(400, 'Ошибка валидации')
    def post(self):
        """
        Метод для приёма данных о новом перевале от мобильного приложения.
        Вызывает метод submit_pereval_data класса PerevalDataManager.
        """
        # Проверяем, что запрос содержит JSON
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 400

        data = request.json

        # Базовая валидация обязательных полей
        required_fields = ['title', 'user', 'coords', 'level']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Вызываем метод класса для обработки данных
        result = data_manager.submit_pereval_data(data)

        # Устанавливаем HTTP-статус в зависимости от результата
        if result['status'] == 'success':
            return jsonify(result), 201  # 201 Created
        else:
            return jsonify(result), 400  # 400 Bad Request


@api.route('/perevals/<int:pereval_id>')
@api.param('pereval_id', 'Идентификатор перевала')
class PerevalDetail(Resource):
    @api.response(200, 'Успешный ответ')
    @api.response(404, 'Перевал не найден')
    def get(self, pereval_id):
        """Получить одну запись (перевал) по её ID."""
        try:
            pereval_data = data_manager.get_pereval_by_id(pereval_id)
            if pereval_data is None:
                return jsonify({'status': 'error', 'message': 'Pereval not found'}), 404
            return jsonify(pereval_data), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @api.expect(pereval_model)
    @api.response(200, 'Успешное обновление')
    @api.response(400, 'Ошибка запроса')
    def patch(self, pereval_id):
        """Редактировать существующую запись, если она в статусе new."""
        if not request.is_json:
            return jsonify({
                'state': 0,
                'message': 'Content-Type must be application/json'
            }), 400

        data = request.json
        try:
            result = data_manager.update_pereval_if_new(pereval_id, data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'state': 0, 'message': str(e)})


@api.route('/user')
class UserPerevals(Resource):
    @api.doc(params={'user__email': 'Email пользователя'})
    @api.response(200, 'Успешный ответ')
    @api.response(400, 'Отсутствует параметр email')
    def get(self):
        """Список данных обо всех объектах, которые пользователь с почтой <email> отправил на сервер."""
        email = request.args.get('user__email')
        if not email:
            return jsonify({'status': 'error', 'message': 'Missing user__email parameter'}), 400

        try:
            perevals = data_manager.get_perevals_by_user_email(email)
            return jsonify({'status': 'success', 'data': perevals}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
