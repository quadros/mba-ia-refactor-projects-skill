"""Orquestra os casos de uso de Task. Reaproveita Task.to_dict()/is_overdue()
em vez de reimplementar a serialização e o cálculo de atraso em cada rota
(eram duplicados em 3 lugares no código legado)."""
from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import process_task_data


def _enriquecer(task):
    data = task.to_dict()
    data['user_name'] = task.user.name if task.user else None
    data['category_name'] = task.category.name if task.category else None
    return data


def listar():
    tasks = Task.query.all()
    return [_enriquecer(t) for t in tasks], 200


def buscar_por_id(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    return task.to_dict(), 200


def criar(dados):
    if not dados:
        return {'error': 'Dados inválidos'}, 400
    if not dados.get('title'):
        return {'error': 'Título é obrigatório'}, 400

    campos, erro = process_task_data(dados)
    if erro:
        return {'error': erro}, 400

    if dados.get('user_id') and not User.query.get(dados['user_id']):
        return {'error': 'Usuário não encontrado'}, 404
    if dados.get('category_id') and not Category.query.get(dados['category_id']):
        return {'error': 'Categoria não encontrada'}, 404

    task = Task()
    task.title = campos['title']
    task.description = campos.get('description', dados.get('description', ''))
    task.status = campos.get('status', 'pending')
    task.priority = campos.get('priority', dados.get('priority', 3))
    task.user_id = dados.get('user_id')
    task.category_id = dados.get('category_id')
    task.due_date = campos.get('due_date')
    task.tags = campos.get('tags')

    db.session.add(task)
    db.session.commit()
    return task.to_dict(), 201


def atualizar(task_id, dados):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    if not dados:
        return {'error': 'Dados inválidos'}, 400

    campos, erro = process_task_data(dados, existing_task=task)
    if erro:
        return {'error': erro}, 400

    if 'user_id' in dados:
        if dados['user_id'] and not User.query.get(dados['user_id']):
            return {'error': 'Usuário não encontrado'}, 404
        task.user_id = dados['user_id']

    if 'category_id' in dados:
        if dados['category_id'] and not Category.query.get(dados['category_id']):
            return {'error': 'Categoria não encontrada'}, 404
        task.category_id = dados['category_id']

    for campo in ('title', 'description', 'status', 'priority', 'due_date', 'tags'):
        if campo in campos:
            setattr(task, campo, campos[campo])

    db.session.commit()
    return task.to_dict(), 200


def deletar(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    db.session.delete(task)
    db.session.commit()
    return {'message': 'Task deletada com sucesso'}, 200


def buscar(query, status, priority, user_id):
    tasks = Task.query
    if query:
        tasks = tasks.filter(
            db.or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%'))
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))

    return [t.to_dict() for t in tasks.all()], 200


def estatisticas():
    total = Task.query.count()
    stats = {
        'total': total,
        'pending': Task.query.filter_by(status='pending').count(),
        'in_progress': Task.query.filter_by(status='in_progress').count(),
        'done': Task.query.filter_by(status='done').count(),
        'cancelled': Task.query.filter_by(status='cancelled').count(),
    }
    overdue = sum(1 for t in Task.query.all() if t.is_overdue())
    stats['overdue'] = overdue
    stats['completion_rate'] = round((stats['done'] / total) * 100, 2) if total > 0 else 0
    return stats, 200
