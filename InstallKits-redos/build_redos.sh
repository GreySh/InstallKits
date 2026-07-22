#!/usr/bin/env bash
#
# Скрипт сборки InstallKits (Tkinter) под Linux / RED OS.
# Запускать из папки проекта:  bash build_redos.sh
#
set -e

APP_NAME="InstallKits"
ENTRY="main.py"

echo "==> Создание виртуального окружения (опционально, но рекомендуется)"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Установка зависимостей"
pip install --upgrade pip
pip install -r requirements-redos.txt

echo "==> Сборка однофайлового исполняемого файла"
pyinstaller --noconfirm --onefile --noconsole \
    --name "$APP_NAME" \
    --add-data "settings.json:." \
    --collect-data customtkinter \
    --hidden-import tkinter \
    --hidden-import tkinter.ttk \
    --hidden-import tinydb \
    "$ENTRY"

echo "==> Копируем settings.json рядом с исполняемым файлом"
cp -f settings.json "dist/settings.json"

echo "==> Готово!"
echo "    Исполняемый файл: dist/$APP_NAME"
echo "    Файл настроек:    dist/settings.json"
echo "    Перенесите ОБА файла вместе на целевой компьютер."
