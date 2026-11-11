from flask import Flask, render_template, jsonify, request, Blueprint, abort, redirect, url_for, flash, g, current_app

import logging
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import time
from datetime import datetime, timedelta, timezone

import src.app.sql_tools as db
import src.app.config as config



def permissionCheckAdmin():
    if request.endpoint == 'admin.admin_login':
        return 
    return permissionCheck('admin_access')

def permissionCheckStudent():
    return permissionCheck('student_access')

def permissionCheck(access_type='student_access'):
    token = request.cookies.get('access_token')
    
    if not token:
        return jsonify({'status': 'error', 'code': 401, "error": "authorization_required", "message": "Missing access token"}), 401
    
    try:
        payload = decode_jwt(token)
    except Exception:
        current_app.logger.exception("Ошибка проверки JWT в permissionCheck")
        return jsonify({'status': 'error', 'code': 401, "error": "authorization_required", "message": "Access token is not valid"}), 401

    if not payload:
        # по хорошему вообще нужно разлогинить пользователя, поскольку вероятно был подделан jwt
        return jsonify({'status': 'error', 'code': 401, "error": "authorization_required", "message": "Access token is not valid2"}), 401
        
    if (payload.get('exp') <= time.time()):
        return jsonify({'status': 'error', 'code': 401, "error": "refresh_required", "message": "Access token is out of date3"}), 401

    if payload.get('type') != access_type:
        return jsonify({'status': 'error', 'code': 403, "error": "forbidden", "message": "insufficient access rights"}), 403

    g.user_id = payload.get('sub')
    g.user_type = payload.get('type')

# registration
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(config.REGI_SECRET_KEY)
    return serializer.dumps(email, salt='email-confirm-salt')

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(config.REGI_SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt='email-confirm-salt',
            max_age=expiration # Ссылка живет 1 час (3600 секунд)
        )
    except (BadSignature, SignatureExpired):
        logging.getLogger(__name__).info("Токен подтверждения email недействителен или просрочен")
        return False
    return email

def manageNewStudent(payload):
    payload['password'] = generate_password_hash(payload['password'])
    db.add_user(payload=payload)
    return generate_confirmation_token(payload["email"])

def namageNewStudentConfirmation(token):

    email = confirm_token(token)
    if not email:
        return False
    with db.get_db_connection() as conn:
        conn.execute(
            "UPDATE students SET is_confirmed = 1 WHERE email = ?",
            (email,)
        )
        conn.commit()
    return True

def manageRotaionJWT(user_id, is_admin=False):
    now = datetime.now(timezone.utc)

    access_payload_type = "admin_access" if is_admin else "student_access"
    access_payload = {
        "sub": str(user_id),
        "type": access_payload_type,
        "exp": now + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now
    }
    access_token = jwt.encode(payload=access_payload, key=config.SECRET_KEY, algorithm=config.ALGORITHM)

    refresh_payload_type = "admin_refresh" if is_admin else "student_refresh"
    refresh_payload = {
        "sub": str(user_id),
        "type": refresh_payload_type,
        "exp": now + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": now
    }
    refresh_token = jwt.encode(payload=refresh_payload, key=config.REFRESH_SECRET, algorithm=config.ALGORITHM)

    db.set_refresh_token(user_id, refresh_token, refresh_payload['exp'].timestamp(), is_admin=is_admin)
    
    return access_token, refresh_token

def manageVerifyStudentOnLogin(payload):
    student = db.get_student_password_by_email(payload["email"])
    if student and check_password_hash(student["password"], payload['password']) and student["is_confirmed"]:
        return student["id"]
    else:
        return None

def manageVerifyAdminOnLogin(payload):
    admin = db.get_admin_password_by_email(payload["email"])
    if admin and check_password_hash(admin["password"], payload['password']):
        return admin["id"]
    else:
        return None

def manageRefresh(refresh_token):
    try:
        payload = decode_jwt(refresh_token, secret_key=config.REFRESH_SECRET, algorithm=config.ALGORITHM)
        user_id = payload["sub"]
    except jwt.ExpiredSignatureError:
        raise Exception("Refresh token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid refresh token")

    refresh_token_data = db.get_refresh_token(user_id, refresh_token)
    if not refresh_token_data: 
        raise Exception("Refresh token revoked or not found")
    
    db.delete_refresh_token(user_id, refresh_token)  

    if refresh_token_data["expires_at"] < datetime.now(timezone.utc):  
        raise Exception("Refresh token revoked or not found")
        
    new_access_token, new_refresh_token = manageRotaionJWT(user_id)

    return new_access_token, new_refresh_token

def decode_jwt(token: str | bytes, 
            secret_key: str = config.SECRET_KEY,
            algorithm: str = config.ALGORITHM) -> str:
    decoded = jwt.decode(token, secret_key, algorithms=[algorithm])
    return decoded

