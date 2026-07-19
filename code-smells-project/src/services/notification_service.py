"""Notificações de domínio (e-mail/SMS/push). Isoladas do controller para
que a orquestração do pedido não precise saber como uma notificação é
enviada — hoje é um log estruturado; trocar por um provedor real não deve
tocar o controller."""
import logging

logger = logging.getLogger(__name__)


def notificar_pedido_criado(pedido_id, usuario_id):
    logger.info("Enviando e-mail: pedido %s criado para usuário %s", pedido_id, usuario_id)
    logger.info("Enviando SMS: seu pedido foi recebido!")
    logger.info("Enviando push: novo pedido recebido pelo sistema")


def notificar_status_pedido(pedido_id, novo_status):
    if novo_status == "aprovado":
        logger.info("Pedido %s foi aprovado! Preparar envio.", pedido_id)
    elif novo_status == "cancelado":
        logger.info("Pedido %s cancelado. Devolver estoque.", pedido_id)
