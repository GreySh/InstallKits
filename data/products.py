"""
Модуль для работы с продуктами (инсталляционными комплектами).
"""

from .db import get_database, get_table
from tinydb import Query


def add_product(name, code='', description=''):
    """
    Добавить новый продукт.
    
    Args:
        name: Название продукта
        code: Код продукта (опционально)
        description: Описание продукта (опционально)
    
    Returns:
        int: ID добавленного продукта
    """
    db = get_database()
    products_table = get_table(db, 'products')
    product_id = products_table.insert({
        'name': name,
        'code': code,
        'description': description
    })
    
    return product_id


def get_all_products():
    """Получить все продукты."""
    db = get_database()
    products_table = get_table(db, 'products')
    return products_table.all()


def get_product_by_id(product_id):
    """Получить продукт по ID."""
    db = get_database()
    products_table = get_table(db, 'products')
    return products_table.get(doc_id=product_id)


def get_product_components(product_id):
    """Получить компоненты продукта."""
    db = get_database()
    kits_table = get_table(db, 'kit_components')
    return kits_table.search(Query().product_id == product_id)


def update_product(product_id, name, code='', description=''):
    """
    Обновить продукт.
    
    Args:
        product_id: ID продукта
        name: Новое название
        code: Новый код (опционально)
        description: Новое описание (опционально)
    """
    db = get_database()
    products_table = get_table(db, 'products')
    products_table.update({
        'name': name,
        'code': code,
        'description': description
    }, doc_ids=[product_id])


def delete_product(product_id):
    """Удалить продукт и его компоненты."""
    db = get_database()
    products_table = get_table(db, 'products')
    kits_table = get_table(db, 'kit_components')
    
    products_table.remove(doc_ids=[product_id])
    kits_table.remove(Query().product_id == product_id)


def add_product_with_components(name, code, description, components):
    """
    Добавить новый продукт с компонентами.
    
    Args:
        name: Название продукта
        code: Код продукта
        description: Описание продукта
        components: Список компонентов в формате [{'disc_id': id, 'disc_quantity': int, 'box_id': id, 'box_quantity': int}, ...]
    
    Returns:
        int: ID добавленного продукта
    """
    db = get_database()
    products_table = get_table(db, 'products')
    product_id = products_table.insert({
        'name': name,
        'code': code,
        'description': description
    })
    
    kits_table = get_table(db, 'kit_components')
    for comp in components:
        kits_table.insert({
            'product_id': product_id,
            'disc_id': comp.get('disc_id'),
            'box_id': comp.get('box_id'),
            'disc_quantity': comp.get('disc_quantity', 0),
            'box_quantity': comp.get('box_quantity', 0)
        })
    
    return product_id


def update_product_with_components(product_id, name, code, description, components):
    """
    Обновить продукт и его компоненты.
    
    Args:
        product_id: ID продукта
        name: Новое название
        code: Новый код
        description: Новое описание
        components: Новый список компонентов
    """
    db = get_database()
    products_table = get_table(db, 'products')
    products_table.update({
        'name': name,
        'code': code,
        'description': description
    }, doc_ids=[product_id])
    
    kits_table = get_table(db, 'kit_components')
    kits_table.remove(Query().product_id == product_id)
    
    for comp in components:
        kits_table.insert({
            'product_id': product_id,
            'disc_id': comp.get('disc_id'),
            'box_id': comp.get('box_id'),
            'disc_quantity': comp.get('disc_quantity', 0),
            'box_quantity': comp.get('box_quantity', 0)
        })
