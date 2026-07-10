"""
Модуль для управления историей операций.
"""

from .db import get_database, get_table
from tinydb import Query
from datetime import datetime


def add_operation(operation_type, product_id, quantity, details=None, operation_date=None):
    """
    Добавить операцию в историю.
    
    Args:
        operation_type: Тип операции ('add_kit', 'dispatch', 'adjust_stock', 'add_disc', 'add_box')
        product_id: ID продукта (если применимо)
        quantity: Количество
        details: Дополнительные данные (опционально)
        operation_date: Дата операции в формате 'YYYY-MM-DD' (опционально, если не указана - текущая дата и время)
    
    Returns:
        int: ID добавленной операции
    """
    db = get_database()
    operations_table = get_table(db, 'operations')
    
    # Если передана дата без времени, добавляем время
    if operation_date:
        if len(operation_date) == 10:  # Формат 'YYYY-MM-DD'
            operation_date = operation_date + ' ' + datetime.now().strftime('%H:%M:%S')
    else:
        operation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return operations_table.insert({
        'operation_type': operation_type,
        'product_id': product_id,
        'quantity': quantity,
        'date': operation_date,
        'details': details or {}
    })


def get_operations(product_id=None, limit=None):
    """
    Получить операции.
    
    Args:
        product_id: ID продукта (если None, вернуть все операции)
        limit: Максимальное количество записей (если None, все)
    
    Returns:
        list: Список операций
    """
    db = get_database()
    operations_table = get_table(db, 'operations')
    
    if product_id:
        results = operations_table.search(Query().product_id == product_id)
    else:
        results = operations_table.all()
    
    # Сортировка по дате (новые первыми)
    results.sort(key=lambda x: x['date'], reverse=True)
    
    if limit:
        results = results[:limit]
    
    return results


def get_operations_by_type(operation_type, limit=None):
    """
    Получить операции по типу.
    
    Args:
        operation_type: Тип операции
        limit: Максимальное количество записей
    
    Returns:
        list: Список операций
    """
    db = get_database()
    operations_table = get_table(db, 'operations')
    
    results = operations_table.search(Query().operation_type == operation_type)
    results.sort(key=lambda x: x['date'], reverse=True)
    
    if limit:
        results = results[:limit]
    
    return results


def delete_operation(operation_id):
    """Удалить операцию по ID."""
    db = get_database()
    operations_table = get_table(db, 'operations')
    operations_table.remove(doc_ids=[operation_id])
