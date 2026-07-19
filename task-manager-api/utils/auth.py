"""Geração/verificação de JWT real. Substitui o token
'fake-jwt-token-' + str(user.id), que não tinha nenhuma propriedade
criptográfica e era trivialmente forjável.
"""
from datetime import timedelta

import jwt

from config.settings import settings
from utils.helpers import utcnow

ALGORITHM = "HS256"


def gerar_token(user):
    payload = {
        "sub": user.id,
        "role": user.role,
        "exp": utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
