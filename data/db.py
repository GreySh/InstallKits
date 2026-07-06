"""
Модуль для работы с базой данных TinyDB.
"""

from tinydb import TinyDB, Query
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'db.json')


def get_db():
    """Получить экземпляр базы данных."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return TinyDB(DB_PATH)


def get_table(db, table_name):
    """Получить таблицу по имени."""
    return db.table(table_name)


# Инициализация при импорте
_db_instance = None


def get_database():
    """Получить глобальный экземпляр базы данных."""
    global _db_instance
    if _db_instance is None:
        _db_instance = get_db()
    return _db_instance


def close_database():
    """Закрыть базу данных и сохранить изменения."""
    global _db_instance
    if _db_instance is not None:
        _db_instance.close()
        _db_instance = None


def clear_database():
    """Очистить всю базу данных (для тестирования)."""
    global _db_instance
    if _db_instance is not None:
        _db_instance.drop_tables()
        _db_instance.close()
        _db_instance = None
