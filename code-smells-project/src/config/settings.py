"""Configuração centralizada da aplicação, lida a partir de variáveis de ambiente.

Nenhum segredo real deve viver aqui como literal — apenas defaults de
desenvolvimento local, nunca usados em produção.
"""
import os


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))


settings = Settings()
