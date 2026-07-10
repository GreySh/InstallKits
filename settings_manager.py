"""
Модуль для управления настройками приложения.
"""

import os
import json
import sys


def get_settings_file():
    """Получить путь к файлу настроек (рядом с executable или в корне проекта)."""
    # Если запущено как .exe файл
    if getattr(sys, 'frozen', False):
        application_dir = os.path.dirname(sys.executable)
        return os.path.join(application_dir, 'settings.json')
    
    # Если запущено как скрипт Python
    return os.path.join(os.path.dirname(__file__), 'settings.json')


# Путь к файлу настроек
SETTINGS_FILE = get_settings_file()

# Глобальный словарь настроек
_settings = None


def load_settings():
    """Загрузить настройки из файла."""
    global _settings
    if _settings is None:
        _settings = {}
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    _settings = data
        except Exception:
            _settings = {}
    return _settings


def save_settings():
    """Сохранить настройки в файл."""
    global _settings
    try:
        settings_dir = os.path.dirname(SETTINGS_FILE)
        if settings_dir and not os.path.exists(settings_dir):
            os.makedirs(settings_dir, exist_ok=True)
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(_settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_setting(key, default=None):
    """Получить значение настройки."""
    load_settings()
    return _settings.get(key, default)


def set_setting(key, value):
    """Установить значение настройки."""
    load_settings()
    _settings[key] = value
    save_settings()


def get_db_path():
    """Получить путь к базе данных."""
    path = get_setting('db_path')
    if path:
        return path
    
    # Если запущено как .exe файл, используем путь относительно exe
    if getattr(sys, 'frozen', False):
        application_dir = os.path.dirname(sys.executable)
        return os.path.join(application_dir, 'data', 'db.json')
    
    # Если запущено как скрипт Python
    return os.path.join(os.path.dirname(__file__), 'data', 'db.json')


def set_db_path(path):
    """Установить путь к базе данных."""
    global _settings
    if _settings is None:
        load_settings()
    _settings['db_path'] = path
    save_settings()
