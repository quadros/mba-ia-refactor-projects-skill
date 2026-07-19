"""Constantes de negócio centralizadas — única fonte de verdade.

Antes espalhadas como listas literais duplicadas em controllers.py.
"""

VALID_CATEGORIES = [
    "informatica", "moveis", "vestuario", "geral", "eletronicos", "livros",
]

VALID_ORDER_STATUSES = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

PRODUCT_NAME_MIN_LENGTH = 2
PRODUCT_NAME_MAX_LENGTH = 200

# Faixas de desconto aplicadas sobre o faturamento bruto no relatório de vendas.
DISCOUNT_TIERS = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]
