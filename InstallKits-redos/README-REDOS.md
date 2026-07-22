# Инструкция по сборке InstallKits (Tkinter) для RED OS

RED OS — это Linux-дистрибутив (совместимый с RHEL/CentOS). Собрать
Linux-исполняемый файл на Windows нельзя (PyInstaller не умеет
кросс-компиляцию), поэтому собирать нужно **на самой машине с RED OS**
(или на Linux с такой же версией glibc). Бинарь, собранный на другом
дистрибутиве, может не запуститься из-за несовпадения версий системных
библиотек.

## Что находится в этой папке

```
InstallKits-redos/
├── main.py                  # точка входа (Tkinter-приложение)
├── settings_manager.py      # работа с settings.json
├── settings.json            # настройки (лежит рядом с exe)
├── requirements-redos.txt    # зависимости Python
├── build_redos.sh           # скрипт сборки
├── data/                    # слой работы с БД (TinyDB)
└── ui/                      # интерфейс (вкладки, диалоги, виджеты)
```

Перенесите ВСЮ папку `InstallKits-redos` на компьютер с RED OS
(например, через флешку, scp или архив).

## Шаг 1. Установка системных зависимостей

Откройте терминал и выполните от имени администратора:

```bash
# Python 3.12+ и Tk (графический toolkit, необходим customtkinter)
sudo dnf install -y python3 python3-tkinter python3-pip python3-virtualenv
# либо, если используется yum:
# sudo yum install -y python3 python3-tkinter python3-pip
```

> Важно: пакет `python3-tkinter` (и системные `tcl`/`tk`) обязателен.
> Без него приложение не запустится с ошибкой про `_tkinter`.

Проверьте версию Python (нужна >= 3.12):

```bash
python3 --version
```

Если в репозиториях RED OS только старая версия Python, установите
3.12 вручную (из исходников или через менеджер версий) — приложение
требует `python = ">=3.12,<3.14"`.

## Шаг 2. Сборка

Перейдите в папку с проектом и запустите скрипт сборки:

```bash
cd InstallKits-redos
bash build_redos.sh
```

Скрипт сам создаст виртуальное окружение `.venv`, установит
зависимости и запустит PyInstaller. В процессе будет собран один
исполняемый файл `dist/InstallKits` и рядом с ним скопирован
`dist/settings.json`.

> Если не хотите использовать виртуальное окружение, можно установить
> зависимости системно (`pip install -r requirements-redos.txt`) и
> запустить сборку вручную:
>
> ```bash
> pyinstaller --noconfirm --onefile --noconsole \
>     --name InstallKits --add-data "settings.json:." \
>     --collect-data customtkinter \
>     --hidden-import tkinter --hidden-import tkinter.ttk --hidden-import tinydb \
>     main.py
> cp settings.json dist/settings.json
> ```

## Шаг 3. Запуск и распространение

Готовые файлы — `dist/InstallKits` (исполняемый) и `dist/settings.json`.
Их нужно держать **в одной папке**.

Для запуска на целевом компьютере просто сделайте файл исполняемым
(если ещё не) и запустите:

```bash
chmod +x dist/InstallKits
./dist/InstallKits
```

Или двойным кликом в файловом менеджере RED OS.

## Где хранится база данных

В `settings.json` ключ `db_path` оставлен пустым, поэтому база данных
создаётся автоматически рядом с исполняемым файлом:
`<папка_с_exe>/data/db.json`.

Чтобы указать свой путь к БД — откройте «Настройки» в самом приложении
либо отредактируйте `settings.json` (поле `db_path`).

## Возможные проблемы

* **Ошибка `No module named '_tkinter'` / `_tkinter.TclError`**
  → не установлен пакет `python3-tkinter` (см. Шаг 1).

* **Окно не появляется / мгновенный выход**
  → убедитесь, что запуск идёт в графической сессии (не в чистой
  консоли без X/Wayland), и что установлены `tcl`/`tk`.

* **Собранный файл не запускается на другом Linux**
  → разные версии glibc. Собирайте непосредственно на RED OS.
