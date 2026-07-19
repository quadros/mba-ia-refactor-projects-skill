from flask import Blueprint, jsonify, request

from controllers import usuario_controller

usuario_bp = Blueprint("usuarios", __name__)


@usuario_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    payload, status = usuario_controller.listar()
    return jsonify(payload), status


@usuario_bp.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscar_usuario(usuario_id):
    payload, status = usuario_controller.buscar_por_id(usuario_id)
    return jsonify(payload), status


@usuario_bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    payload, status = usuario_controller.criar(request.get_json())
    return jsonify(payload), status


@usuario_bp.route("/login", methods=["POST"])
def login():
    payload, status = usuario_controller.login(request.get_json())
    return jsonify(payload), status
