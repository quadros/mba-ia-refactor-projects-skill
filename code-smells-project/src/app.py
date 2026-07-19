"""Composition root: monta a aplicação Flask. Nenhuma regra de negócio
mora aqui — apenas configuração, registro de blueprints e middlewares.

Os endpoints administrativos inseguros do código legado (`/admin/query`,
que executava SQL arbitrário do body sem autenticação, e `/admin/reset-db`,
que apagava todo o banco sem autenticação) foram removidos nesta
refatoração: eram a própria vulnerabilidade CRITICAL reportada na
auditoria (ver reports/audit-project-1.md), não uma feature legítima a
preservar.
"""
import logging

from flask import Flask
from flask_cors import CORS

from config.database import get_db
from config.settings import settings
from middlewares.error_handler import register_error_handlers
from views.misc_routes import misc_bp
from views.pedido_routes import pedido_bp
from views.produto_routes import produto_bp
from views.usuario_routes import usuario_bp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app)

    app.register_blueprint(misc_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)

    register_error_handlers(app)

    return app


app = create_app()

if __name__ == "__main__":
    get_db()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{settings.PORT}")
    print("=" * 50)

    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
