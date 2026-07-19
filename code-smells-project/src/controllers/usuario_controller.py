"""Orquestra os casos de uso de Usuário (cadastro e autenticação)."""
from models import usuario_model


def listar():
    return {"dados": usuario_model.get_todos(), "sucesso": True}, 200


def buscar_por_id(usuario_id):
    usuario = usuario_model.get_por_id(usuario_id)
    if not usuario:
        return {"erro": "Usuário não encontrado"}, 404
    return {"dados": usuario, "sucesso": True}, 200


def criar(dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        return {"erro": "Nome, email e senha são obrigatórios"}, 400

    usuario_id = usuario_model.criar(nome, email, senha)
    return {"dados": {"id": usuario_id}, "sucesso": True}, 201


def login(dados):
    email = dados.get("email", "") if dados else ""
    senha = dados.get("senha", "") if dados else ""

    if not email or not senha:
        return {"erro": "Email e senha são obrigatórios"}, 400

    usuario = usuario_model.autenticar(email, senha)
    if not usuario:
        return {"erro": "Email ou senha inválidos", "sucesso": False}, 401

    return {"dados": usuario, "sucesso": True, "mensagem": "Login OK"}, 200
