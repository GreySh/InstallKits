"""
Модуль для работы с базой данных TinyDB.
"""

from tinydb import TinyDB, Query
import os

# Импортируем настройки
try:
    from settings_manager import get_db_path, set_db_path
except:
    # Если settings_manager не найден, использовать путь по умолчанию
    def get_db_path():
        return os.path.join(os.path.dirname(__file__), 'data', 'db.json')
    def set_db_path(path):
        pass

# Инициализация при импорте
_db_instance = None
_db_path = None


def get_db_path_actual():
    """Получить текущий путь к базе данных (с проверкой перенастройки)."""
    global _db_path
    new_path = get_db_path()
    if _db_path != new_path:
        _db_path = new_path
    return _db_path


def get_db():
    """Получить экземпляр базы данных."""
    db_path = get_db_path_actual()
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    return TinyDB(db_path, encoding='utf-8')


def get_table(db, table_name):
    """Получить таблицу по имени."""
    return db.table(table_name)


def get_database():
    """Получить глобальный экземпляр базы данных."""
    global _db_instance
    global _db_path
    new_path = get_db_path_actual()
    if _db_instance is None or _db_path != new_path:
        if _db_instance is not None:
            _db_instance.close()
        _db_path = new_path
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
