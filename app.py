from flask import Flask, render_template, jsonify, request, Blueprint, abort, redirect, url_for
import time
import sqlite3
import src.config as config
import src.tokens as tokens
import requests
import json

app = Flask(__name__, template_folder='src/templates', static_folder='src/static')

admin_bp = Blueprint('admin', __name__)
api_bp = Blueprint('api', __name__)

def get_db_connection():
    conn = sqlite3.connect('mydatabase.db')
    conn.row_factory = sqlite3.Row
    return conn


def check_api_key():
    # Пропускаем проверку для маршрута логина
    if request.endpoint == 'admin.admin_login':
        return
    if request.endpoint == 'api.admin_login_api':
        return
        
    token = request.cookies.get('access_token')
    if not token:
        # abort(401, description="INVALID API KEY")
        return redirect(url_for('admin.admin_login'))

    try:
    
        payload = tokens.decode_jwt(token)

    except Exception as e:
        return redirect(url_for('admin.admin_login'))


    if not payload:
        # abort(401, description="INVALID API KEY")
        return redirect(url_for('admin.admin_login'))
        
    if (payload.get('exp') <= time.time()):
        # abort(403, description="TOKEN EXPIRED")
        return redirect(url_for('admin.admin_login'))
    pass




@app.route("/")
def index():
    """Главная страница - расписание уроков"""
    return render_template('index.html')

@app.route("/successfulPayment")
def successful_payment():
    """Страница успешного платежа"""
    return render_template('successful_payment.html')

@app.route("/unsuccessfulPayment")
def unsuccessful_payment():
    """Страница неудачного платежа"""
    return render_template('unsuccessful_payment.html')

@app.route('/privacy')
def privacy():
    """Страница политики конфиденциальности"""
    return render_template('privacy.html')





@admin_bp.route("/login")
def admin_login():
    """Страница входа в админ панель"""
    return render_template('admin_login.html')

@admin_bp.route("/panel")
def admin_panel():
    """Админ панель для управления данными"""
    return render_template('admin_panel.html')





@api_bp.route("/login", methods=['POST'])
def admin_login_api():
    """API для авторизации администратора"""
    try:
        data = request.get_json()
        password = data.get('password', '')

        # Простая проверка пароля (в будущем можно заменить на более безопасную)
        if password == config.ADMIN_PASS:

            payload = {
                'exp': int(time.time()) + config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                'iat': int(time.time()),
                'sub': 'admin'
            }
            
            token = tokens.encode_jwt(payload)
            
            response = jsonify({
                'status': 'success',
                'code': 200,
                'message': 'Login successful'
            })
            response.set_cookie('access_token', token, httponly=True, max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
            return response, 200
        else:
            return jsonify({
                'status': 'error',
                'code': 401,
                'message': 'Invalid password'
            }), 401

    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Ошибка сервера'}), 500


# образец json который нужно распарсить
# {
#     "status": "success",
#     "result": {
#         "uuid": "INV-89UX09KA",
#         "created": "2026-01-27 09:03:58.958133",
#         "address": "0xb07427fc721C23674c48233ffE93D3846ee58B63",
#         "expiry_date": "2026-01-28 09:03:57.493361",
#         "side_commission": "client",
#         "side_commission_service": "merchant",
#         "type_payments": "crypto",
#         "amount": 0.034187,
#         "amount_usd": 100.0,
#         "amount_in_fiat": 100.0,
#         "fee": 1.499999996212864e-06,
#         "fee_usd": 0.0,
#         "service_fee": 0.00065,
#         "service_fee_usd": 1.9,
#         "fiat_currency": "USD",
#         "status": "created",
#         "is_email_required": false,
#         "link": "https://pay.trybit.com/89UX09KA",
#         "invoice_id": null,
#         "currency": {
#             "id": 3,
#             "code": "ETH",
#             "fullcode": "ETH",
#             "network": {
#                 "code": "ERC20",
#                 "id": 3,
#                 "icon": "https://cdn.trybit.com/img/network/ERC.svg",
#                 "fullname": "Ethereum"
#             },
#             "name": "Ethereum",
#             "is_email_required": false,
#             "stablecoin": false,
#             "icon_base": "https://cdn.trybit.com/img/currency/ETH.svg",
#             "icon_network": "https://cdn.trybit.com/img/currency/ETH.svg",
#             "icon_qr": "https://cdn.trybit.com/img/stroke/ETH_STROKE.svg",
#             "order": 9
#         },
#         "project": {
#             "id": 1,
#             "name": "Test",
#             "fail": "https://test.com/failed-payment",
#             "success": "https://test.com/successful-payment",
#             "logo": "https://static.trybit.com/logo/L52hWwjt98uYtUF91765782359.174416.jpg"
#         },
#         "test_mode": false
#     }
# }

def save_invoice_data(data):
    """Сохранить callback от CryptoCloud в таблицу automatic_postback и обновить статус счета."""
    if not isinstance(data, dict):
        return

    result = data.get('result', data)
    invoice_uuid = (result.get('uuid') or data.get('uuid') or data.get('invoice_uuid') or '').strip()
    amount = result.get('amount', data.get('amount'))
    amount_usd = result.get('amount_usd', data.get('amount_usd'))
    amount_in_fiat = result.get('amount_in_fiat', data.get('amount_in_fiat'))
    currency = result.get('currency')
    if isinstance(currency, dict):
        currency_name = currency.get('code') or currency.get('fullcode') or currency.get('name') or ''
    else:
        currency_name = currency or ''
    status = data.get('status') or result.get('status') or 'unknown'
    invoice_id = result.get('invoice_id') or data.get('invoice_id')
    created = result.get('created') or data.get('created')
    address = result.get('address') or data.get('address')
    expiry_date = result.get('expiry_date') or data.get('expiry_date')
    invoice_status = result.get('status') or data.get('status') or status
    is_email_required = result.get('is_email_required', data.get('is_email_required'))
    link = result.get('link') or data.get('link')
    project = result.get('project') or {}
    project_name = project.get('name') if isinstance(project, dict) else ''
    test_mode = result.get('test_mode', data.get('test_mode'))

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO automatic_postback (
                status,
                invoice_id,
                amount_crypto,
                amount_usd,
                amount_in_fiat,
                currency,
                invoice_uuid,
                invoice_created,
                invoice_address,
                invoice_expiry_date,
                invoice_status,
                invoice_is_email_required,
                invoice_link,
                invoice_project_name,
                invoice_test_mode,
                raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                status,
                invoice_id,
                amount,
                amount_usd,
                amount_in_fiat,
                currency_name,
                invoice_uuid,
                created,
                address,
                expiry_date,
                invoice_status,
                1 if is_email_required else 0,
                link,
                project_name,
                1 if test_mode else 0,
                json.dumps(data, ensure_ascii=False)
            )
        )
        conn.commit()

    if invoice_uuid:
        with get_db_connection() as conn:
            matches = conn.execute(
                "SELECT id FROM invoice_creation_responses WHERE uuid = ? ORDER BY id DESC",
                (invoice_uuid,)
            ).fetchall()
            if len(matches) == 1:
                conn.execute(
                    "UPDATE invoice_creation_responses SET isPaid = 1 WHERE uuid = ?",
                    (invoice_uuid,)
                )
                conn.commit()


@app.route("/invoicecallback", methods=['POST'])
def invoice_callback():
    """Обработка callback от CryptoCloud"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

        save_invoice_data(data)

        return jsonify({'status': 'success', 'message': 'Callback received'}), 200
    except Exception as e:
        print(f"Error processing invoice callback: {e}")
        return jsonify({'status': 'error', 'message': 'Server error'}), 500

@api_bp.route("/new-invoice", methods=['POST'])
def new_invoice(): # DOUBlE CHECK REQUEST

    baseURL = "https://api.cryptocloud.plus/v2/invoice/create"
    cryptocloudAPIKey = config.CRYPTOCLOUD_APIKEY
    request_data = request.get_json(silent=True) or {}
    student_id = request_data.get("studentId")
    amount = request_data.get("amount")

    headers = {
        "Authorization": f"Token {cryptocloudAPIKey}",
        "Content-Type": "application/json"
    }

    data = {
        "amount": amount,
        "shop_id": config.CRYPTOCLOUD_SHOP_ID,
        "currency": "USD",
        "add_fields": {
            "time_to_pay": { "hours": 24, "minutes": 0},
            "available_currencies": [ "USDT_TRC20"],
            "cryptocurrency": "USDT_TRC20"
        }
    }

    response = requests.post(baseURL, headers=headers, json=data)
    data = response.json()
    formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
    if response.status_code == 200:
        print("Success:", formatted_json)
        result = data.get("result", {})
        try:
            student_id = int(student_id) if student_id is not None else None
        except (TypeError, ValueError):
            student_id = None

        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO invoice_creation_responses (
                    student_id,
                    status,
                    uuid,
                    created,
                    expiry_date,
                    amount,
                    amount_usd,
                    amount_in_fiat,
                    fiat_currency,
                    invoice_status,
                    is_email_required,
                    link,
                    invoice_id,
                    test_mode,
                    isPaid
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    student_id,
                    data.get("status") or result.get("status") or "created",
                    result.get("uuid"),
                    result.get("created"),
                    result.get("expiry_date"),
                    result.get("amount"),
                    result.get("amount_usd"),
                    result.get("amount_in_fiat"),
                    result.get("fiat_currency"),
                    result.get("status"),
                    1 if result.get("is_email_required") else 0,
                    result.get("link"),
                    result.get("invoice_id"),
                    1 if result.get("test_mode") else 0
                )
            )
            conn.commit()
    else:
        print("Fail:", response.status_code, response.text)

    return jsonify({ "link": data["result"]["link"]})


@api_bp.route("/admin/students", methods=['GET'])
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
    except Exception as exc:
        print(f"Error fetching students: {exc}")
        return jsonify([])


@api_bp.route("/admin/invoices", methods=['GET'])
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
    except Exception as exc:
        print(f"Error fetching invoices: {exc}")
        return jsonify([])


@api_bp.route("/admin/students", methods=['POST'])
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
    except Exception as exc:
        print(f"Error creating student: {exc}")
        return jsonify({'status': 'error', 'message': 'Ошибка при создании студента'}), 500


@api_bp.route("/admin/students/<int:student_id>", methods=['PUT'])
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
    except Exception as exc:
        print(f"Error updating student: {exc}")
        return jsonify({'status': 'error', 'message': 'Ошибка при обновлении студента'}), 500


@api_bp.route("/payments", methods=['GET'])
def get_payments():
    """Получить платежи"""
    return jsonify([
        {"id": 1, "student": 1, "sum": 5000.00}
    ])


admin_bp.before_request(check_api_key)
api_bp.before_request(check_api_key)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(api_bp, url_prefix='/api')