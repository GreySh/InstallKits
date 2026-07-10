# Инструкция по сборке исполняемого файла

## Требования

- Python 3.12 (не 3.13 или 3.14, так как PyInstaller не поддерживает эти версии)
- Poetry (для управления зависимостями)

## Шаги по сборке

### 1. Установка зависимостей

```bash
# Установите Python 3.12 если его нет
# Создайте виртуальное окружение с Python 3.12
D:\Python312\python.exe -m venv .venv312

# Активируйте виртуальное окружение
.venv312\Scripts\activate

# Установите poetry если её нет
pip install poetry

# Используйте poetry для создания среды и установки зависимостей
poetry env use .venv312\Scripts\python.exe
poetry lock
poetry install
```

### 2. Сборка .exe файла

```bash
# Используйте poetry для запуска pyinstaller
poetry run pyinstaller --onefile --windowed --name InstallKits main.py

# Или используйте уже созданный spec-файл
poetry run pyinstaller installkits.spec
```

### 3. Результат

После успешной сборки исполняемый файл будет находиться в папке `dist/`:
- `dist/InstallKits.exe` - готовый исполняемый файл (примерно 12 МБ)

## Публикация

Файл `InstallKits.exe` можно распространять на любые системы Windows без необходимости установки Python или зависимостей.

## Примечания

- Исполняемый файл содержит все необходимые библиотеки (CustomTkinter, TinyDB, OpenPyXL)
- Файл не требует установки Python на целевой машине
- При первом запуске антивирус может сканировать файл - это нормально для новых .exe файлов
