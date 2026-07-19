"""Tratamento de erro e logging centralizados.

Substitui os blocos `try/except Exception` repetidos em cada função de
controller do código legado: qualquer exceção não tratada por um handler
específico cai aqui, é logada com stacktrace e vira uma resposta HTTP
padronizada — em vez de vazar `str(e)` para o cliente.
"""
import logging

from flask import jsonify

logger = logging.getLogger("code_smells_project")


def register_error_handlers(app):
    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        logger.exception("Erro não tratado ao processar requisição")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
