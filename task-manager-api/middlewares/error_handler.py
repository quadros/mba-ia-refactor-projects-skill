"""Tratamento de erro e logging centralizados. Substitui os `except:`
genéricos espalhados pelas rotas, que engoliam qualquer exceção e sempre
respondiam a mesma mensagem sem logar a causa raiz.
"""
import logging

from flask import jsonify

logger = logging.getLogger("task_manager_api")


def register_error_handlers(app):
    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        logger.exception("Erro não tratado ao processar requisição")
        return jsonify({"error": "Erro interno"}), 500
