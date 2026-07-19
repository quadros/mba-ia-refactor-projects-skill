"""Acesso a dados de Usuário. Senhas nunca trafegam em texto puro no banco."""
from werkzeug.security import check_password_hash, generate_password_hash

from config.database import get_db


def _row_to_dict(row, include_senha=False):
    data = {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }
    if include_senha:
        data["senha"] = row["senha"]
    return data


def get_todos():
    db = get_db()
    rows = db.execute("SELECT * FROM usuarios").fetchall()
    return [_row_to_dict(row) for row in rows]


def get_por_id(usuario_id):
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return _row_to_dict(row) if row else None


def get_por_email(email):
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    return row


def criar(nome, email, senha, tipo="cliente"):
    db = get_db()
    senha_hash = generate_password_hash(senha)
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid


def autenticar(email, senha):
    row = get_por_email(email)
    if row and check_password_hash(row["senha"], senha):
        return _row_to_dict(row)
    return None
