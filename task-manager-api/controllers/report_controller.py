"""Relatórios agregados. A produtividade por usuário antes disparava uma
query Task.query.filter_by(user_id=u.id) por usuário dentro de um loop
Python (N+1); agora é uma única query agregada com GROUP BY."""
from datetime import timedelta

from sqlalchemy import case, func

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import utcnow


def _produtividade_por_usuario():
    rows = (
        db.session.query(
            User.id,
            User.name,
            func.count(Task.id).label('total'),
            func.sum(case((Task.status == 'done', 1), else_=0)).label('completed'),
        )
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id)
        .all()
    )

    stats = []
    for user_id, user_name, total, completed in rows:
        completed = completed or 0
        stats.append({
            'user_id': user_id,
            'user_name': user_name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
        })
    return stats


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    tasks_by_status = {
        'pending': Task.query.filter_by(status='pending').count(),
        'in_progress': Task.query.filter_by(status='in_progress').count(),
        'done': Task.query.filter_by(status='done').count(),
        'cancelled': Task.query.filter_by(status='cancelled').count(),
    }

    tasks_by_priority = {
        'critical': Task.query.filter_by(priority=1).count(),
        'high': Task.query.filter_by(priority=2).count(),
        'medium': Task.query.filter_by(priority=3).count(),
        'low': Task.query.filter_by(priority=4).count(),
        'minimal': Task.query.filter_by(priority=5).count(),
    }

    overdue_tasks = [t for t in Task.query.filter(Task.due_date.isnot(None)).all() if t.is_overdue()]
    overdue_list = [{
        'id': t.id,
        'title': t.title,
        'due_date': str(t.due_date),
        'days_overdue': (utcnow() - t.due_date).days,
    } for t in overdue_tasks]

    seven_days_ago = utcnow() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == 'done', Task.updated_at >= seven_days_ago
    ).count()

    report = {
        'generated_at': str(utcnow()),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': tasks_by_status,
        'tasks_by_priority': tasks_by_priority,
        'overdue': {'count': len(overdue_list), 'tasks': overdue_list},
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': _produtividade_por_usuario(),
    }
    return report, 200


def user_report(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    counts = {'done': 0, 'pending': 0, 'in_progress': 0, 'cancelled': 0}
    overdue = 0
    high_priority = 0

    for t in tasks:
        counts[t.status] = counts.get(t.status, 0) + 1
        if t.priority <= 2:
            high_priority += 1
        if t.is_overdue():
            overdue += 1

    total = len(tasks)
    report = {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            **counts,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((counts['done'] / total) * 100, 2) if total > 0 else 0,
        },
    }
    return report, 200
