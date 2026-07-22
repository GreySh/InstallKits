"""
Модуль для управления составом комплектов.
"""

from .db import get_database, get_table
from tinydb import Query


def add_kit_component(product_id, disc_id, box_id, disc_quantity=0, box_quantity=0):
    """
    Добавить компонент в состав комплекта.
    
    Args:
        product_id: ID продукта
        disc_id: ID диска (None если диск не используется)
        box_id: ID коробки (None если коробка не используется)
        disc_quantity: Количество дисков
        box_quantity: Количество коробок
    
    Returns:
        int: ID добавленного компонента
    """
    db = get_database()
    kits_table = get_table(db, 'kit_components')
    
    return kits_table.insert({
        'product_id': product_id,
        'disc_id': disc_id,
        'box_id': box_id,
        'disc_quantity': disc_quantity,
        'box_quantity': box_quantity
    })


def update_kit_component(component_id, disc_id, box_id, disc_quantity=0, box_quantity=0):
    """
    Обновить компонент комплекта.
    
    Args:
        component_id: ID компонента
        disc_id: ID диска
        box_id: ID коробки
        disc_quantity: Количество дисков
        box_quantity: Количество коробок
    """
    db = get_database()
    kits_table = get_table(db, 'kit_components')
    
    kits_table.update({
        'disc_id': disc_id,
        'box_id': box_id,
        'disc_quantity': disc_quantity,
        'box_quantity': box_quantity
    }, doc_ids=[component_id])


def delete_kit_component(component_id):
    """Удалить компонент из состава комплекта."""
    db = get_database()
    kits_table = get_table(db, 'kit_components')
    kits_table.remove(doc_ids=[component_id])


def get_kit_components(product_id):
    """Получить все компоненты продукта."""
    db = get_database()
    kits_table = get_table(db, 'kit_components')
    return kits_table.search(Query().product_id == product_id)


def get_kit_component(component_id):
    """Получить компонент по ID."""
    db = get_database()
    kits_table = get_table(db, 'kit_components')
    return kits_table.get(doc_id=component_id)
