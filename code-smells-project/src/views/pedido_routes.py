from flask import Blueprint, jsonify, request

from controllers import pedido_controller

pedido_bp = Blueprint("pedidos", __name__)


@pedido_bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    payload, status = pedido_controller.criar(request.get_json())
    return jsonify(payload), status


@pedido_bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    payload, status = pedido_controller.listar_todos()
    return jsonify(payload), status


@pedido_bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    payload, status = pedido_controller.listar_por_usuario(usuario_id)
    return jsonify(payload), status


@pedido_bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    novo_status = (request.get_json() or {}).get("status", "")
    payload, status = pedido_controller.atualizar_status(pedido_id, novo_status)
    return jsonify(payload), status


@pedido_bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    payload, status = pedido_controller.relatorio_vendas()
    return jsonify(payload), status
