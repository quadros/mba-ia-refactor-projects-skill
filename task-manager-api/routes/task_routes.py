from flask import Blueprint, jsonify, request

from controllers import task_controller

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    payload, status = task_controller.listar()
    return jsonify(payload), status


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    payload, status = task_controller.buscar_por_id(task_id)
    return jsonify(payload), status


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    payload, status = task_controller.criar(request.get_json())
    return jsonify(payload), status


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    payload, status = task_controller.atualizar(task_id, request.get_json())
    return jsonify(payload), status


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    payload, status = task_controller.deletar(task_id)
    return jsonify(payload), status


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    payload, status = task_controller.buscar(
        query=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=request.args.get('priority', ''),
        user_id=request.args.get('user_id', ''),
    )
    return jsonify(payload), status


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    payload, status = task_controller.estatisticas()
    return jsonify(payload), status
