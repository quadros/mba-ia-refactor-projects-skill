"""Orquestra os casos de uso de Usuário, incluindo autenticação com JWT real."""
from database import db
from models.task import Task
from models.user import User
from utils.auth import gerar_token
from utils.helpers import VALID_ROLES, validate_email


def listar():
    result = []
    for u in User.query.all():
        data = u.to_dict()
        data['task_count'] = len(u.tasks)
        result.append(data)
    return result, 200


def buscar_por_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return data, 200


def criar(dados):
    if not dados:
        return {'error': 'Dados inválidos'}, 400

    name = dados.get('name')
    email = dados.get('email')
    password = dados.get('password')
    role = dados.get('role', 'user')

    if not name:
        return {'error': 'Nome é obrigatório'}, 400
    if not email:
        return {'error': 'Email é obrigatório'}, 400
    if not password:
        return {'error': 'Senha é obrigatória'}, 400
    if not validate_email(email):
        return {'error': 'Email inválido'}, 400
    if len(password) < 4:
        return {'error': 'Senha deve ter no mínimo 4 caracteres'}, 400
    if User.query.filter_by(email=email).first():
        return {'error': 'Email já cadastrado'}, 409
    if role not in VALID_ROLES:
        return {'error': 'Role inválido'}, 400

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 201


def atualizar(user_id, dados):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404
    if not dados:
        return {'error': 'Dados inválidos'}, 400

    if 'name' in dados:
        user.name = dados['name']

    if 'email' in dados:
        if not validate_email(dados['email']):
            return {'error': 'Email inválido'}, 400
        existing = User.query.filter_by(email=dados['email']).first()
        if existing and existing.id != user_id:
            return {'error': 'Email já cadastrado'}, 409
        user.email = dados['email']

    if 'password' in dados:
        if len(dados['password']) < 4:
            return {'error': 'Senha muito curta'}, 400
        user.set_password(dados['password'])

    if 'role' in dados:
        if dados['role'] not in VALID_ROLES:
            return {'error': 'Role inválido'}, 400
        user.role = dados['role']

    if 'active' in dados:
        user.active = dados['active']

    db.session.commit()
    return user.to_dict(), 200


def deletar(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    for task in Task.query.filter_by(user_id=user_id).all():
        db.session.delete(task)

    db.session.delete(user)
    db.session.commit()
    return {'message': 'Usuário deletado com sucesso'}, 200


def tasks_do_usuario(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    return [t.to_dict() for t in tasks], 200


def login(dados):
    if not dados:
        return {'error': 'Dados inválidos'}, 400

    email = dados.get('email')
    password = dados.get('password')
    if not email or not password:
        return {'error': 'Email e senha são obrigatórios'}, 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return {'error': 'Credenciais inválidas'}, 401
    if not user.active:
        return {'error': 'Usuário inativo'}, 403

    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': gerar_token(user),
    }, 200
