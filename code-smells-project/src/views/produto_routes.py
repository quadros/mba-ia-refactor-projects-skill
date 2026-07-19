from flask import Blueprint, jsonify, request

from controllers import produto_controller

produto_bp = Blueprint("produtos", __name__)


@produto_bp.route("/produtos", methods=["GET"])
def listar_produtos():
    payload, status = produto_controller.listar()
    return jsonify(payload), status


@produto_bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    payload, status = produto_controller.buscar(
        termo=request.args.get("q", ""),
        categoria=request.args.get("categoria"),
        preco_min=request.args.get("preco_min"),
        preco_max=request.args.get("preco_max"),
    )
    return jsonify(payload), status


@produto_bp.route("/produtos/<int:produto_id>", methods=["GET"])
def buscar_produto(produto_id):
    payload, status = produto_controller.buscar_por_id(produto_id)
    return jsonify(payload), status


@produto_bp.route("/produtos", methods=["POST"])
def criar_produto():
    payload, status = produto_controller.criar(request.get_json())
    return jsonify(payload), status


@produto_bp.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto(produto_id):
    payload, status = produto_controller.atualizar(produto_id, request.get_json())
    return jsonify(payload), status


@produto_bp.route("/produtos/<int:produto_id>", methods=["DELETE"])
def deletar_produto(produto_id):
    payload, status = produto_controller.deletar(produto_id)
    return jsonify(payload), status
