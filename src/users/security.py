"""Хэширование паролей и токены сессий. Только стандартная библиотека."""

import hashlib
import hmac
import secrets

# Параметры scrypt: n=2**14, r=8, p=1 (рекомендация OWASP для scrypt)
_N, _R, _P = 2**14, 8, 1


def _scrypt(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=32)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    return f"{salt.hex()}${_scrypt(password, salt).hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt_hex, _, hash_hex = stored.partition("$")
    expected = _scrypt(password, bytes.fromhex(salt_hex))
    return hmac.compare_digest(expected.hex(), hash_hex)


def new_token() -> str:
    return secrets.token_urlsafe(32)


# Хэш случайного пароля: проверяем его, когда пользователя нет,
# чтобы такой ответ шёл столько же, сколько ответ на неверный пароль
DUMMY_HASH = hash_password(secrets.token_urlsafe(16))
