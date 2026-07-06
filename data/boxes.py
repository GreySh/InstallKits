"""
Модуль для работы с коробками.
"""

from .db import get_database, get_table
from tinydb import Query


def add_box(name, quantity=0):
    """
    Добавить новую коробку.
    
    Args:
        name: Название коробки (должно быть уникальным)
        quantity: Количество (по умолчанию 0)
    
    Returns:
        int: ID добавленной коробки
    """
    db = get_database()
    boxes_table = get_table(db, 'boxes')
    
    # Проверка на уникальность
    if boxes_table.search(Query().name == name):
        raise ValueError(f"Коробка с названием '{name}' уже существует")
    
    box_id = boxes_table.insert({'name': name})
    
    stock_table = get_table(db, 'stock_boxes')
    stock_table.insert({'box_id': box_id, 'quantity': quantity})
    
    return box_id


def get_all_boxes():
    """Получить все коробки."""
    db = get_database()
    boxes_table = get_table(db, 'boxes')
    return boxes_table.all()


def get_box_by_id(box_id):
    """Получить коробку по ID."""
    db = get_database()
    boxes_table = get_table(db, 'boxes')
    return boxes_table.get(doc_id=box_id)


def get_box_by_name(name):
    """Получить коробку по названию."""
    db = get_database()
    boxes_table = get_table(db, 'boxes')
    return boxes_table.get(Query().name == name)


def update_box(box_id, name):
    """
    Обновить название коробки.
    
    Args:
        box_id: ID коробки
        name: Новое название
    """
    db = get_database()
    boxes_table = get_table(db, 'boxes')
    
    # Проверка на уникальность нового названия
    existing = boxes_table.get(Query().name == name)
    if existing and existing.doc_id != box_id:
        raise ValueError(f"Коробка с названием '{name}' уже существует")
    
    boxes_table.update({'name': name}, doc_ids=[box_id])


def delete_box(box_id):
    """Удалить коробку."""
    db = get_database()
    boxes_table = get_table(db, 'boxes')
    stock_table = get_table(db, 'stock_boxes')
    
    boxes_table.remove(doc_ids=[box_id])
    stock_table.remove(Query().box_id == box_id)
