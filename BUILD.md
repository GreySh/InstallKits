# Сборка InstallKits

Инструкция по сборке **десктопного** приложения в исполняемый файл Windows (`.exe`).

Веб-версия (`webapp/`) отдельно не упаковывается — для неё достаточно `poetry run python webapp/app.py`.

## Требования

| Компонент | Версия |
|-----------|--------|
| Python | 3.12 или 3.13 |
| Poetry | 1.8+ |
| ОС для сборки | Windows |

> Python 3.14+ пока не рекомендуется — возможны проблемы совместимости с PyInstaller.

## Подготовка окружения

```bash
cd InstallKits
poetry install
```

Poetry создаёт виртуальное окружение в папке `.venv` (настроено в `poetry.toml`).

Проверка:

```powershell
poetry run python --version
poetry run pyinstaller --version
```

### Альтернатива: ручное создание `.venv`

```powershell
py -3.12 -m venv .venv
poetry env use .venv\Scripts\python.exe
poetry install
```

## Сборка .exe (Windows)

### Рекомендуемый способ — через spec-файл

```bash
poetry run pyinstaller installkits.spec
```

Файл `installkits.spec` уже настроен:
- точка входа: `main.py`
- режим: однофайловый исполняемый (`--onefile`)
- без консольного окна (`console=False`)

### Альтернативный способ — командная строка

```bash
poetry run pyinstaller --onefile --windowed --name InstallKits main.py
```

## Результат сборки

После успешной сборки:

```
dist/
└── InstallKits.exe      # готовый исполняемый файл (~15–25 МБ)

build/                   # временные файлы PyInstaller (можно удалить)
```

Папки `build/`, `dist/` и `*.exe` перечислены в `.gitignore`.

## Распространение

Скопируйте на целевую машину:

```
InstallKits.exe
settings.json          # опционально, для начальных настроек
```

При первом запуске `.exe` приложение попытается скопировать `settings.json` рядом с исполняемым файлом, если файл настроек ещё не существует.

### Настройка базы данных

В `settings.json` укажите путь к базе данных:

```json
{
  "db_path": "data/db.json"
}
```

Для сетевого хранения:

```json
{
  "db_path": "//server/share/db_IK.json"
}
```

Путь можно изменить в приложении на вкладке **«Настройки»**.

## Что входит в .exe

- CustomTkinter (GUI)
- TinyDB (работа с JSON-базой)
- openpyxl (экспорт отчётов в Excel)
- Все модули `data/` и `ui/`

Flask и веб-интерфейс в `.exe` **не включаются**.

## Устранение неполадок

### `ModuleNotFoundError` при запуске собранного .exe

Пересоберите с явным указанием скрытых импортов в `installkits.spec`:

```python
hiddenimports=['customtkinter', 'tinydb', 'openpyxl'],
```

### Антивирус блокирует .exe

Нормально для свежесобранных PyInstaller-файлов. Добавьте в исключения или подпишите исполняемый файл.

### Ошибка при `poetry install`

Убедитесь, что используется Python 3.12 или 3.13:

```powershell
poetry env use C:\Path\To\Python312\python.exe
poetry install
```

### База данных не найдена

Проверьте `settings.json` рядом с `InstallKits.exe` и доступность пути в `db_path`.

## Сборка для Linux

Для Linux используйте отдельные инструкции:

- **Архив с исходниками:** `./package_linux.sh` — создаёт `InstallKits_linux.tar.gz`
- **RPM-пакет:** см. [RPM_PACKAGING.md](RPM_PACKAGING.md)

На Linux `.exe` не собирается — запуск через `python main.py` или собственный пакет.

## См. также

- [README.md](README.md) — общее описание проекта
- [RPM_PACKAGING.md](RPM_PACKAGING.md) — сборка RPM для Linux
- [webapp/README.md](webapp/README.md) — веб-версия
