"""
Модуль для работы с дисками.
"""

from .db import get_database, get_table
from tinydb import Query


def add_disc(name, quantity=0):
    """
    Добавить новый диск.
    
    Args:
        name: Название диска (должно быть уникальным)
        quantity: Количество (по умолчанию 0)
    
    Returns:
        int: ID добавленного диска
    """
    db = get_database()
    discs_table = get_table(db, 'discs')
    
    # Проверка на уникальность
    if discs_table.search(Query().name == name):
        raise ValueError(f"Диск с названием '{name}' уже существует")
    
    disc_id = discs_table.insert({'name': name})
    
    stock_table = get_table(db, 'stock_discs')
    stock_table.insert({'disc_id': disc_id, 'quantity': quantity})
    
    return disc_id


def get_all_discs():
    """Получить все диски."""
    db = get_database()
    discs_table = get_table(db, 'discs')
    return discs_table.all()


def get_disc_by_id(disc_id):
    """Получить диск по ID."""
    db = get_database()
    discs_table = get_table(db, 'discs')
    return discs_table.get(doc_id=disc_id)


def get_disc_by_name(name):
    """Получить диск по названию."""
    db = get_database()
    discs_table = get_table(db, 'discs')
    return discs_table.get(Query().name == name)


def update_disc(disc_id, name):
    """
    Обновить название диска.
    
    Args:
        disc_id: ID диска
        name: Новое название
    """
    db = get_database()
    discs_table = get_table(db, 'discs')
    
    # Проверка на уникальность нового названия
    existing = discs_table.get(Query().name == name)
    if existing and existing.doc_id != disc_id:
        raise ValueError(f"Диск с названием '{name}' уже существует")
    
    discs_table.update({'name': name}, doc_ids=[disc_id])


def delete_disc(disc_id):
    """Удалить диск."""
    db = get_database()
    discs_table = get_table(db, 'discs')
    stock_table = get_table(db, 'stock_discs')
    
    discs_table.remove(doc_ids=[disc_id])
    stock_table.remove(Query().disc_id == disc_id)