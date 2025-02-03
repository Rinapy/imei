from typing import Any, Literal
import jwt
from datetime import datetime, timedelta, UTC

from infrastructure.settings import SECRET_KEY


def generate_jwt(user_id: int, source: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.now(UTC) + timedelta(hours=12),  # Срок действия токена
        'iat': datetime.now(UTC),  # Время создания
        'iss': source  # Источник токена
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_jwt(token: str) -> Any | Literal['Token has expired'] | Literal['Invalid token']:
    try:
        # Логируем начало токена для отладки
        print(f"Decoding token: {token[:20]}...")
        decoded_payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"],
            # Явно указываем проверку срока действия
            options={"verify_exp": True}
        )
        # Логируем результат для отладки
        print(f"Decoded payload: {decoded_payload}")
        return decoded_payload
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError as e:
        print(f"Invalid token error: {str(e)}")  # Логируем ошибку для отладки
        return "Invalid token"
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Логируем неожиданные ошибки
        return "Invalid token"
