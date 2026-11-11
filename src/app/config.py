"""Database configuration module"""
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL connection settings
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'engwithluv')

ALGORITHM = os.getenv('ALGORITHM', 'HS256')
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
REFRESH_SECRET = os.getenv('REFRESH_SECRET', 'your-refresh-secret-key')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))

ADMIN_PASS = os.getenv('ADMIN_PASS', 'admin123')
# Format: postgresql://user:password@host:port/database
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


CRYPTOCLOUD_APIKEY = os.getenv('CRYPTOCLOUD_APIKEY', 'your-cryptocloud-apikey')
CRYPTOCLOUD_SHOP_ID = os.getenv('CRYPTOCLOUD_SHOP_ID', 'your-cryptocloud-shop-id')

MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'True').lower() in ['true', '1', 't']
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
MAIL_SENDER = os.getenv('MAIL_SENDER', '')
MAIL_SENDER_NAME = os.getenv('MAIL_SENDER_NAME', '')
REGI_SECRET_KEY = os.getenv('REGI_SECRET_KEY', '')


