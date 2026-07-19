"""Acesso a dados de Pedido. Listagens usam JOIN em vez de queries N+1."""
from config.constants import DISCOUNT_TIERS
from config.database import get_db


def _linhas_para_pedidos(rows):
    """Agrupa linhas de um JOIN pedido+itens+produto em uma lista de pedidos aninhados."""
    pedidos_por_id = {}
    ordem = []
    for row in rows:
        pedido_id = row["id"]
        if pedido_id not in pedidos_por_id:
            pedidos_por_id[pedido_id] = {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            ordem.append(pedido_id)
        if row["item_produto_id"] is not None:
            pedidos_por_id[pedido_id]["itens"].append({
                "produto_id": row["item_produto_id"],
                "produto_nome": row["produto_nome"] or "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return [pedidos_por_id[pid] for pid in ordem]


_PEDIDOS_JOIN_SQL = """
    SELECT
        p.id, p.usuario_id, p.status, p.total, p.criado_em,
        ip.produto_id AS item_produto_id, ip.quantidade, ip.preco_unitario,
        pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = ip.produto_id
"""


def get_por_usuario(usuario_id):
    db = get_db()
    rows = db.execute(
        _PEDIDOS_JOIN_SQL + " WHERE p.usuario_id = ? ORDER BY p.id",
        (usuario_id,),
    ).fetchall()
    return _linhas_para_pedidos(rows)


def get_todos():
    db = get_db()
    rows = db.execute(_PEDIDOS_JOIN_SQL + " ORDER BY p.id").fetchall()
    return _linhas_para_pedidos(rows)


def criar(usuario_id, itens):
    db = get_db()
    total = 0
    produtos_cache = {}

    for item in itens:
        produto = db.execute(
            "SELECT * FROM produtos WHERE id = ?", (item["produto_id"],)
        ).fetchone()
        if produto is None:
            return {"erro": f"Produto {item['produto_id']} não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}
        produtos_cache[item["produto_id"]] = produto
        total += produto["preco"] * item["quantidade"]

    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    pedido_id = cursor.lastrowid

    for item in itens:
        produto = produtos_cache[item["produto_id"]]
        db.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
        )
        db.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"]),
        )

    db.commit()
    return {"pedido_id": pedido_id, "total": total}


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()
    return True


def _calcular_desconto(faturamento):
    for limite, percentual in DISCOUNT_TIERS:
        if faturamento > limite:
            return faturamento * percentual
    return 0


def relatorio_vendas():
    db = get_db()

    total_pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT SUM(total) FROM pedidos").fetchone()[0] or 0
    pendentes = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = ?", ("pendente",)
    ).fetchone()[0]
    aprovados = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = ?", ("aprovado",)
    ).fetchone()[0]
    cancelados = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = ?", ("cancelado",)
    ).fetchone()[0]

    desconto = _calcular_desconto(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
