import jwt
import bcrypt
import src.config as settings

def encode_jwt(payload:dict,
            secret_key: str = settings.SECRET_KEY,
            algorithm: str = settings.ALGORITHM) -> str:
    encoded = jwt.encode(payload, secret_key, algorithm=algorithm)
    return encoded

def decode_jwt(token: str | bytes, 
            secret_key: str = settings.SECRET_KEY,
            algorithm: str = settings.ALGORITHM) -> str:
    decoded = jwt.decode(token, secret_key, algorithms=[algorithm])
    return decoded