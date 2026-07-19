"""Configuração centralizada, lida de variáveis de ambiente.

Antes: SECRET_KEY hardcoded em app.py e credenciais SMTP hardcoded em
services/notification_service.py.
"""
import os


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///tasks.db")

    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")

    JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", "8"))


settings = Settings()
