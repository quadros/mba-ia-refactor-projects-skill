"""Orquestra os casos de uso de Pedido, incluindo o efeito colateral de
notificação — delegado ao service, nunca implementado inline aqui."""
from config.constants import VALID_ORDER_STATUSES
from models import pedido_model
from services import notification_service


def criar(dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        return {"erro": "Usuario ID é obrigatório"}, 400
    if not itens:
        return {"erro": "Pedido deve ter pelo menos 1 item"}, 400

    resultado = pedido_model.criar(usuario_id, itens)
    if "erro" in resultado:
        return {"erro": resultado["erro"], "sucesso": False}, 400

    notification_service.notificar_pedido_criado(resultado["pedido_id"], usuario_id)

    return {
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }, 201


def listar_por_usuario(usuario_id):
    return {"dados": pedido_model.get_por_usuario(usuario_id), "sucesso": True}, 200


def listar_todos():
    return {"dados": pedido_model.get_todos(), "sucesso": True}, 200


def atualizar_status(pedido_id, novo_status):
    if novo_status not in VALID_ORDER_STATUSES:
        return {"erro": "Status inválido"}, 400

    pedido_model.atualizar_status(pedido_id, novo_status)
    notification_service.notificar_status_pedido(pedido_id, novo_status)

    return {"sucesso": True, "mensagem": "Status atualizado"}, 200


def relatorio_vendas():
    return {"dados": pedido_model.relatorio_vendas(), "sucesso": True}, 200
