from flask import Blueprint, jsonify, request

from controllers import category_controller, report_controller

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    payload, status = report_controller.summary_report()
    return jsonify(payload), status


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    payload, status = report_controller.user_report(user_id)
    return jsonify(payload), status


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    payload, status = category_controller.listar()
    return jsonify(payload), status


@report_bp.route('/categories', methods=['POST'])
def create_category():
    payload, status = category_controller.criar(request.get_json())
    return jsonify(payload), status


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    payload, status = category_controller.atualizar(cat_id, request.get_json())
    return jsonify(payload), status


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    payload, status = category_controller.deletar(cat_id)
    return jsonify(payload), status
