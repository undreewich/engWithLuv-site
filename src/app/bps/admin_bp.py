from flask import Flask, current_app, render_template, jsonify, request, Blueprint, abort, redirect, url_for, flash

import src.app.accessManager as ACM
import src.app.config as config
from src.app.sql_tools import get_db_connection

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/panel", methods=['GET'])
def admin_panel():
    return render_template('admin_panel.html')

@admin_bp.route("/login", methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')

    try:
        payload = request.get_json(silent=True) or request.form.to_dict()
        if not (user_id := ACM.manageVerifyAdminOnLogin(payload=payload)):
            return jsonify({'status': 'error', 'code': 401, "error": "no_such_user", "message": "need to contact administration"}), 401

        access_token, refresh_token = ACM.manageRotaionJWT(user_id, is_admin=True)

        response = jsonify({'status': 'success', 'code': 200, "error": "", 'message': 'successful login'})
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite='Lax', max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite='Lax', max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        
        return response, 200

    except Exception:
        current_app.logger.exception("Непредвиденная ошибка при входе администратора")
        return jsonify({'status': 'error', 'message': 'server error'}), 500

@admin_bp.route("/admin/students", methods=['GET'])
def get_students():
    """Получить список студентов постранично"""
    try:
        limit = request.args.get('limit', default=50, type=int)
        offset = request.args.get('offset', default=0, type=int)

        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0

        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    id,
                    name,
                    surname,
                    email,
                    lessons_repaid AS prepaidLessonsCount,
                    lessons_done AS doneLessonsCount,
                    cash_prepaid AS prepaidSum,
                    cash_done AS usedSum,
                    is_active AS isActive,
                    age
                FROM students
                ORDER BY id DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            ).fetchall()
        return jsonify([dict(row) for row in rows])
    except Exception:
        current_app.logger.exception("Не удалось загрузить список учеников в админ-панели")
        return jsonify([])

@admin_bp.route("/admin/invoices", methods=['GET'])
def get_invoices():
    """Получить счета по студентам постранично"""
    try:
        limit = request.args.get('limit', default=50, type=int)
        offset = request.args.get('offset', default=0, type=int)

        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0

        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    icr.id,
                    students.id AS student_id,
                    (students.name || ' ' || students.surname) AS student,
                    icr.amount,
                    icr.isPaid,
                    icr.created,
                    icr.expiry_date,
                    icr.link
                FROM invoice_creation_responses icr
                LEFT JOIN students ON students.id = icr.student_id
                ORDER BY icr.id DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            ).fetchall()
        return jsonify([dict(row) for row in rows])
    except Exception:
        current_app.logger.exception("Не удалось загрузить счета в админ-панели")
        return jsonify([])

@admin_bp.route("/admin/students", methods=['POST'])
def create_student():
    """Создать нового студента"""
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    surname = (data.get('surname') or '').strip()
    email = (data.get('email') or '').strip()
    age = data.get('age')

    if not name or not surname or not email or age is None:
        return jsonify({'status': 'error', 'message': 'Заполните имя, фамилию, email и возраст'}), 400

    try:
        age = int(age)
    except (TypeError, ValueError):
        return jsonify({'status': 'error', 'message': 'Возраст должен быть числом'}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO students (name, surname, email, lessons_repaid, lessons_done, cash_prepaid, cash_done, is_active, age)
                VALUES (?, ?, ?, 0, 0, 0, 0, 1, ?)
                """,
                (name, surname, email, age)
            )
            conn.commit()
            student_id = cursor.lastrowid
        return jsonify({
            'status': 'success',
            'message': 'Студент добавлен',
            'id': student_id
        }), 201
    except Exception:
        current_app.logger.exception("Не удалось создать ученика")
        return jsonify({'status': 'error', 'message': 'Ошибка при создании студента'}), 500

@admin_bp.route("/admin/students/<int:student_id>", methods=['PUT'])
def update_student(student_id):
    """Обновить данные студента из модального окна"""
    data = request.get_json(silent=True) or {}

    name = (data.get('name') or '').strip()
    surname = (data.get('surname') or '').strip()
    email = (data.get('email') or '').strip()
    age = data.get('age')
    prepaid_lessons = data.get('prepaidLessonsCount')
    done_lessons = data.get('doneLessonsCount')
    prepaid_sum = data.get('prepaidSum')
    used_sum = data.get('usedSum')
    is_active = data.get('isActive')

    if not name or not surname or not email or age is None:
        return jsonify({'status': 'error', 'message': 'Заполните имя, фамилию, email и возраст'}), 400

    try:
        age = int(age)
        prepaid_lessons = int(prepaid_lessons) if prepaid_lessons is not None else 0
        done_lessons = int(done_lessons) if done_lessons is not None else 0
        prepaid_sum = float(prepaid_sum) if prepaid_sum is not None else 0.0
        used_sum = float(used_sum) if used_sum is not None else 0.0
        is_active = bool(is_active) if isinstance(is_active, bool) else str(is_active).lower() == 'true'
    except (TypeError, ValueError):
        return jsonify({'status': 'error', 'message': 'Некорректные значения полей'}), 400


    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE students
                SET name = ?,
                    surname = ?,
                    email = ?,
                    lessons_repaid = ?,
                    lessons_done = ?,
                    cash_prepaid = ?,
                    cash_done = ?,
                    is_active = ?,
                    age = ?
                WHERE id = ?
                """,
                (name, surname, email, prepaid_lessons, done_lessons, prepaid_sum, used_sum, 1 if is_active else 0, age, student_id)
            )
            conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'status': 'error', 'message': 'Студент не найден'}), 404

        return jsonify({'status': 'success', 'message': 'Данные студента обновлены'}), 200
    except Exception:
        current_app.logger.exception("Не удалось обновить данные ученика id=%s", student_id)
        return jsonify({'status': 'error', 'message': 'Ошибка при обновлении студента'}), 500

@admin_bp.route("/payments", methods=['GET'])
def get_payments():
    """Получить платежи"""
    return jsonify([
        {"id": 1, "student": 1, "sum": 5000.00}
    ])



@admin_bp.route("/new-invoice", methods=['POST'])
def new_invoice(): # DOUBlE CHECK REQUEST
    return jsonify({'status': 'error', 'message': 'server error'}), 500 #Debugging line
    # baseURL = "https://api.trybit.com/v2/invoice/create"
    # cryptocloudAPIKey = config.CRYPTOCLOUD_APIKEY
    # request_data = request.get_json(silent=True) or {}
    # student_id = request_data.get("studentId")
    # amount = request_data.get("amount")

    # headers = {
    #     "Authorization": f"Token {cryptocloudAPIKey}",
    #     "Content-Type": "application/json"
    # }

    # data = {
    #     "amount": amount,
    #     "shop_id": config.CRYPTOCLOUD_SHOP_ID,
    #     "currency": "USD",
    #     "add_fields": {
    #         "time_to_pay": { "hours": 24, "minutes": 0},
    #         "available_currencies": [ "USDT_TRC20"],
    #         "cryptocurrency": "USDT_TRC20"
    #     }
    # }

    # response = requests.post(baseURL, headers=headers, json=data)
    # data = response.json()
    # formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
    # if response.status_code == 200:
    #     print("Success:", formatted_json)
    #     result = data.get("result", {})
    #     try:
    #         student_id = int(student_id) if student_id is not None else None
    #     except (TypeError, ValueError):
    #         student_id = None

    #     with get_db_connection() as conn:
    #         conn.execute(
    #             """
    #             INSERT INTO invoice_creation_responses (
    #                 student_id,
    #                 status,
    #                 uuid,
    #                 created,
    #                 expiry_date,
    #                 amount,
    #                 amount_usd,
    #                 amount_in_fiat,
    #                 fiat_currency,
    #                 invoice_status,
    #                 is_email_required,
    #                 link,
    #                 invoice_id,
    #                 test_mode,
    #                 isPaid
    #             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    #             """,
    #             (
    #                 student_id,
    #                 data.get("status") or result.get("status") or "created",
    #                 result.get("uuid"),
    #                 result.get("created"),
    #                 result.get("expiry_date"),
    #                 result.get("amount"),
    #                 result.get("amount_usd"),
    #                 result.get("amount_in_fiat"),
    #                 result.get("fiat_currency"),
    #                 result.get("status"),
    #                 1 if result.get("is_email_required") else 0,
    #                 result.get("link"),
    #                 result.get("invoice_id"),
    #                 1 if result.get("test_mode") else 0
    #             )
    #         )
    #         conn.commit()
    # else:
    #     print("Fail:", response.status_code, response.text)

    # return jsonify({ "link": data["result"]["link"]})