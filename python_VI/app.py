from flask import Flask, request, jsonify
from data_manager import PerevalDataManager
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env
load_dotenv()

app = Flask(__name__)
data_manager = PerevalDataManager()

@app.route('/submitData', methods=['POST'])
def submit_data():
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


@app.route('/submitData/<int:pereval_id>', methods=['GET'])
def get_pereval(pereval_id):
    """Получить одну запись (перевал) по её ID."""
    try:
        pereval_data = data_manager.get_pereval_by_id(pereval_id)
        if pereval_data is None:
            return jsonify({'status': 'error', 'message': 'Pereval not found'}), 404
        return jsonify(pereval_data), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/submitData/<int:pereval_id>', methods=['PATCH'])
def update_pereval(pereval_id):
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


@app.route('/submitData/', methods=['GET'])
def get_perevals_by_email():
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
    app.run(host='0.0.0.0', port=5000, debug=True)



