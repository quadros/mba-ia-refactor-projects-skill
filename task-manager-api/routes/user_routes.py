from flask import Blueprint, jsonify, request

from controllers import user_controller

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    payload, status = user_controller.listar()
    return jsonify(payload), status


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    payload, status = user_controller.buscar_por_id(user_id)
    return jsonify(payload), status


@user_bp.route('/users', methods=['POST'])
def create_user():
    payload, status = user_controller.criar(request.get_json())
    return jsonify(payload), status


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    payload, status = user_controller.atualizar(user_id, request.get_json())
    return jsonify(payload), status


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    payload, status = user_controller.deletar(user_id)
    return jsonify(payload), status


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    payload, status = user_controller.tasks_do_usuario(user_id)
    return jsonify(payload), status


@user_bp.route('/login', methods=['POST'])
def login():
    payload, status = user_controller.login(request.get_json())
    return jsonify(payload), status
