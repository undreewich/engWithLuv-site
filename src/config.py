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
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))


ADMIN_PASS = os.getenv('ADMIN_PASS', 'admin123')
# Format: postgresql://user:password@host:port/database
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


CRYPTOCLOUD_APIKEY = os.getenv('CRYPTOCLOUD_APIKEY', 'your-cryptocloud-apikey')
CRYPTOCLOUD_SHOP_ID = os.getenv('CRYPTOCLOUD_SHOP_ID', 'your-cryptocloud-shop-id')


