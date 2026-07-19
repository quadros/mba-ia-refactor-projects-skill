"""Orquestra os casos de uso de Produto. Sem SQL, sem conhecimento de HTTP
além de receber dados já parseados pela View e devolver (payload, status)."""
from config.constants import (
    PRODUCT_NAME_MAX_LENGTH,
    PRODUCT_NAME_MIN_LENGTH,
    VALID_CATEGORIES,
)
from models import produto_model


def _validar_produto(dados):
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            return f"{campo.capitalize()} é obrigatório"

    nome = dados["nome"]
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        return "Preço não pode ser negativo"
    if estoque < 0:
        return "Estoque não pode ser negativo"
    if len(nome) < PRODUCT_NAME_MIN_LENGTH:
        return "Nome muito curto"
    if len(nome) > PRODUCT_NAME_MAX_LENGTH:
        return "Nome muito longo"
    if categoria not in VALID_CATEGORIES:
        return f"Categoria inválida. Válidas: {VALID_CATEGORIES}"
    return None


def listar():
    return {"dados": produto_model.get_todos(), "sucesso": True}, 200


def buscar_por_id(produto_id):
    produto = produto_model.get_por_id(produto_id)
    if not produto:
        return {"erro": "Produto não encontrado", "sucesso": False}, 404
    return {"dados": produto, "sucesso": True}, 200


def criar(dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400

    erro = _validar_produto(dados)
    if erro:
        return {"erro": erro}, 400

    produto_id = produto_model.criar(
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return {"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}, 201


def atualizar(produto_id, dados):
    if not produto_model.get_por_id(produto_id):
        return {"erro": "Produto não encontrado"}, 404
    if not dados:
        return {"erro": "Dados inválidos"}, 400

    erro = _validar_produto(dados)
    if erro:
        return {"erro": erro}, 400

    produto_model.atualizar(
        produto_id,
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return {"sucesso": True, "mensagem": "Produto atualizado"}, 200


def deletar(produto_id):
    if not produto_model.get_por_id(produto_id):
        return {"erro": "Produto não encontrado"}, 404
    produto_model.deletar(produto_id)
    return {"sucesso": True, "mensagem": "Produto deletado"}, 200


def buscar(termo, categoria, preco_min, preco_max):
    if preco_min is not None:
        preco_min = float(preco_min)
    if preco_max is not None:
        preco_max = float(preco_max)
    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return {"dados": resultados, "total": len(resultados), "sucesso": True}, 200
