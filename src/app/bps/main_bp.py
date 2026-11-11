from flask import Blueprint, current_app, render_template, jsonify, request, abort, redirect, url_for, flash


import src.app.config as config
import src.app.accessManager as ACM
from src.app.mailService import sendRegistrationConfirmationEmail

# Создаем blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    """Главная страница - расписание уроков"""
    return render_template('index.html')

@main_bp.route("/successfulPayment")
def successful_payment():
    """Страница успешного платежа"""
    return render_template('successful_payment.html')

@main_bp.route("/unsuccessfulPayment")
def unsuccessful_payment():
    """Страница неудачного платежа"""
    return render_template('unsuccessful_payment.html')

@main_bp.route('/privacy')
def privacy():
    """Страница политики конфиденциальности"""
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    """Страница пользовательского соглашения"""
    return render_template('terms.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        payload = request.get_json(silent=True) or request.form.to_dict()

        emailConfirmToken = ACM.manageNewStudent(payload=payload)
        sendRegistrationConfirmationEmail(payload["email"], emailConfirmToken)
        
        flash('На вашу почту отправлено письмо для подтверждения.', 'info')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main_bp.route('/confirm/<token>')
def confirm_email(token):
    if ACM.namageNewStudentConfirmation(token):
        return redirect(url_for('main.login'))
    else:
        flash('Ссылка подтверждения недействительна или просрочена.', 'danger')
        return redirect(url_for('main.index'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            payload = request.get_json(silent=True) or request.form.to_dict()
            if not (user_id := ACM.manageVerifyStudentOnLogin(payload=payload)):
                if not request.is_json:
                    flash('Неверный email или пароль.', 'danger')
                    return redirect(url_for('main.login'))
                return jsonify({'status': 'error', 'code': 401, 'message': 'unsuccessful login'}), 401

            access_token, refresh_token = ACM.manageRotaionJWT(user_id)

            response = jsonify({'status': 'success', 'code' : 200, 'message': 'successful login'})
            response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite='Lax', max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
            response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite='Lax', max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
            return response, 200

        except Exception:
            current_app.logger.exception("Непредвиденная ошибка при входе ученика")
            return jsonify({'status': 'error', 'message': 'server error'}), 500
    return render_template('login.html')

@main_bp.route('/refresh', methods=['POST'])
def refresh_access_token():
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        response = jsonify({"status": "error", "message": "Authentication required"})
        response.delete_cookie('refresh_token', path='/', secure=True, httponly=True, samesite='Lax')
        response.delete_cookie('access_token', path='/', secure=True, httponly=True, samesite='Lax')
        return response, 401

    try:
        new_access_token, new_refresh_token = ACM.manageRefresh(refresh_token)
    except Exception:
        current_app.logger.exception("Не удалось обновить токен доступа")
        response = jsonify({"status": "error", "message": "Authentication required"})
        response.delete_cookie('refresh_token', path='/', secure=True, httponly=True, samesite='Lax')
        response.delete_cookie('access_token', path='/', secure=True, httponly=True, samesite='Lax')
        return response, 401

    response = jsonify({'status': 'success', 'code' : 200, 'message': 'successful refresh'})
    response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True, secure=True, samesite='Lax', max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
    response.set_cookie(key="access_token", value=new_access_token, httponly=True, secure=True, samesite='Lax', max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return response, 200
    
@main_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    pass

@main_bp.route('/logout', methods=['GET'])
def logout():
    refresh_token = request.cookies.get('refresh_token')
    try:
        ACM.logout_user(refresh_token=refresh_token, is_admin=False)
    except Exception:
        current_app.logger.exception("Не удалось отозвать refresh-токен при выходе")

    flash('Вы успешно вышли из системы.', 'success')
    response = redirect(url_for('main.index'))
    response.delete_cookie('refresh_token', path='/', secure=True, httponly=True, samesite='Lax')
    response.delete_cookie('access_token', path='/', secure=True, httponly=True, samesite='Lax')
    return response


