from database import db
from models.category import Category
from models.task import Task


def listar():
    result = []
    for c in Category.query.all():
        data = c.to_dict()
        data['task_count'] = Task.query.filter_by(category_id=c.id).count()
        result.append(data)
    return result, 200


def criar(dados):
    if not dados:
        return {'error': 'Dados inválidos'}, 400

    name = dados.get('name')
    if not name:
        return {'error': 'Nome é obrigatório'}, 400

    category = Category()
    category.name = name
    category.description = dados.get('description', '')
    category.color = dados.get('color', '#000000')

    db.session.add(category)
    db.session.commit()
    return category.to_dict(), 201


def atualizar(cat_id, dados):
    cat = Category.query.get(cat_id)
    if not cat:
        return {'error': 'Categoria não encontrada'}, 404
    if not dados:
        return {'error': 'Dados inválidos'}, 400

    if 'name' in dados:
        cat.name = dados['name']
    if 'description' in dados:
        cat.description = dados['description']
    if 'color' in dados:
        cat.color = dados['color']

    db.session.commit()
    return cat.to_dict(), 200


def deletar(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        return {'error': 'Categoria não encontrada'}, 404

    db.session.delete(cat)
    db.session.commit()
    return {'message': 'Categoria deletada'}, 200
