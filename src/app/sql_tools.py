import sqlite3


def get_db_connection():
    conn = sqlite3.connect('mydatabase.db')
    conn.row_factory = sqlite3.Row
    return conn


def add_user(payload):
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO students (
                name,
                surname,
                email,
                lessons_prepaid,
                lessons_done,
                cash_prepaid,
                cash_done,
                is_active,
                age,
                password,
                is_confirmed 
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload['first_name'],
                    payload['last_name'],
                    payload['email'],
                    0,  # lessons_prepaid
                    0,  # lessons_done
                    0.0,  # cash_prepaid
                    0.0,  # cash_done
                    1,  # is_active
                    payload['age'],
                    payload['password'],
                    False
                )
            )
            conn.commit()

def get_user_by_email(email):
    with get_db_connection() as conn:
        user = conn.execute(
            "SELECT * FROM students WHERE email = ?",
            (email,)
        ).fetchone()
    return user

def get_student_password_by_email(email):
    return get_user_password_by_email(email, 'students')

def get_admin_password_by_email(email):
    return get_user_password_by_email(email, 'admins')

def get_user_password_by_email(email, user_type):
    with get_db_connection() as conn:
        user = conn.execute(
            f"SELECT id, password, is_confirmed FROM {user_type} WHERE email = ?",
            (email,)
        ).fetchone()
    return user if user else None

def set_refresh_token(user_id, refresh_token, expires_at, is_admin=False):
    table_name = 'refresh_tokens_admins' if is_admin else 'refresh_tokens'
    with get_db_connection() as conn:
        conn.execute(
            f"INSERT INTO {table_name} (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user_id, refresh_token, expires_at)
        )
        conn.commit()

def get_refresh_token(user_id, refresh_token, is_admin=False):
    table_name = 'refresh_tokens_admins' if is_admin else 'refresh_tokens'
    with get_db_connection() as conn:
        token = conn.execute(
            f"SELECT * FROM {table_name} WHERE user_id = ? AND token = ?",
            (user_id, refresh_token)
        ).fetchone()
    return token if token else None

def delete_refresh_token(user_id, refresh_token, is_admin=False):
    table_name = 'refresh_tokens_admins' if is_admin else 'refresh_tokens'
    with get_db_connection() as conn:
        conn.execute(
            f"DELETE FROM {table_name} WHERE user_id = ? AND token = ?",
            (user_id, refresh_token)
        )
        conn.commit()