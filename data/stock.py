"""
Модуль для управления остатками.
"""

from .db import get_database, get_table
from tinydb import Query


def get_stock_disc_quantity(disc_id):
    """Получить количество дисков на остатке."""
    db = get_database()
    stock_table = get_table(db, 'stock_discs')
    record = stock_table.get(Query().disc_id == disc_id)
    return record['quantity'] if record else 0


def get_stock_box_quantity(box_id):
    """Получить количество коробок на остатке."""
    db = get_database()
    stock_table = get_table(db, 'stock_boxes')
    record = stock_table.get(Query().box_id == box_id)
    return record['quantity'] if record else 0


def adjust_stock_disc(disc_id, new_quantity):
    """
    Корректировка остатка дисков.
    
    Args:
        disc_id: ID диска
        new_quantity: Новое количество (должно быть >= 0)
    
    Returns:
        bool: True если успешно, False если диска нет
    """
    db = get_database()
    stock_table = get_table(db, 'stock_discs')
    
    record = stock_table.get(Query().disc_id == disc_id)
    if not record:
        return False
    
    if new_quantity < 0:
        raise ValueError("Количество не может быть отрицательным")
    
    stock_table.update({'quantity': new_quantity}, doc_ids=[record.doc_id])
    return True


def adjust_stock_box(box_id, new_quantity):
    """
    Корректировка остатка коробок.
    
    Args:
        box_id: ID коробки
        new_quantity: Новое количество (должно быть >= 0)
    
    Returns:
        bool: True если успешно, False если коробки нет
    """
    db = get_database()
    stock_table = get_table(db, 'stock_boxes')
    
    record = stock_table.get(Query().box_id == box_id)
    if not record:
        return False
    
    if new_quantity < 0:
        raise ValueError("Количество не может быть отрицательным")
    
    stock_table.update({'quantity': new_quantity}, doc_ids=[record.doc_id])
    return True


def add_stock_disc(disc_id, quantity):
    """Добавить диски на остаток."""
    if quantity <= 0:
        raise ValueError("Количество должно быть положительным")
    
    current = get_stock_disc_quantity(disc_id)
    return adjust_stock_disc(disc_id, current + quantity)


def add_stock_box(box_id, quantity):
    """Добавить коробки на остаток."""
    if quantity <= 0:
        raise ValueError("Количество должно быть положительным")
    
    current = get_stock_box_quantity(box_id)
    return adjust_stock_box(box_id, current + quantity)


def get_all_stock_discs():
    """Получить все остатки дисков с информацией о дисках."""
    db = get_database()
    stock_table = get_table(db, 'stock_discs')
    discs_table = get_table(db, 'discs')
    
    result = []
    for record in stock_table.all():
        disc = discs_table.get(doc_id=record['disc_id'])
        if disc:
            result.append({
                'disc_id': record['disc_id'],
                'disc_name': disc['name'],
                'quantity': record['quantity']
            })
    return result


def get_all_stock_boxes():
    """Получить все остатки коробок с информацией о коробках."""
    db = get_database()
    stock_table = get_table(db, 'stock_boxes')
    boxes_table = get_table(db, 'boxes')
    
    result = []
    for record in stock_table.all():
        box = boxes_table.get(doc_id=record['box_id'])
        if box:
            result.append({
                'box_id': record['box_id'],
                'box_name': box['name'],
                'quantity': record['quantity']
            })
    return result
