import flet as ft
import os
from settings_manager import get_db_path, set_db_path, SETTINGS_FILE


class SettingsView:
    def __init__(self, app):
        self.app = app
        self.page = app.page
        self.db_path_field = None

    def refresh(self):
        pass

    def build(self):
        header = ft.Text("Настройки", size=24, weight=ft.FontWeight.BOLD)

        current_path = get_db_path()
        self.db_path_field = ft.TextField(
            label="Путь к базе данных",
            value=current_path,
            expand=True,
        )

        browse_btn = ft.FilledButton("Обзор", icon=ft.Icons.FOLDER_OPEN, on_click=self.browse_db)

        save_db_btn = ft.FilledButton("Сохранить путь к БД", icon=ft.Icons.SAVE, on_click=self.save_db_path)

        db_section = ft.Column([
            ft.Text("База данных", size=18, weight=ft.FontWeight.BOLD),
            ft.Text(f"Текущий файл настроек: {SETTINGS_FILE}", size=12, color=ft.Colors.GREY),
            ft.Row([self.db_path_field, browse_btn, save_db_btn], spacing=10),
            ft.Text("Укажите путь к файлу базы данных TinyDB (.json). Можно использовать локальный путь или сетевой UNC-путь (\\\\server\\share\\db.json).", size=12, color=ft.Colors.GREY, italic=True),
        ])

        info_section = ft.Column([
            ft.Text("О программе", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("InstallKits — программа для учёта инсталляционных комплектов."),
            ft.Text("Версия: 0.1.0"),
            ft.Text("Интерфейс: Flet"),
            ft.Text("База данных: TinyDB"),
        ])

        return ft.Column([
            header,
            ft.Divider(),
            db_section,
            ft.Divider(height=20),
            info_section,
        ], expand=True, scroll=ft.ScrollMode.AUTO)

    async def browse_db(self, e):
        file_picker = ft.FilePicker()
        self.page.overlay.append(file_picker)
        self.page.update()
        files = await file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["json"],
            dialog_title="Выберите файл базы данных",
        )
        if files:
            self.db_path_field.value = files[0].path
            self.page.update()

    def save_db_path(self, e):
        path = self.db_path_field.value.strip()
        if not path:
            self.page.show_dialog(ft.SnackBar(ft.Text("Укажите путь к базе данных"), bgcolor=ft.Colors.ORANGE))
            return

        db_dir = os.path.dirname(path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except Exception as ex:
                self.page.show_dialog(ft.SnackBar(ft.Text(f"Не удалось создать директорию: {ex}"), bgcolor=ft.Colors.RED))
                return

        try:
            set_db_path(path)
            self.page.show_dialog(ft.SnackBar(
                ft.Text("Путь к БД сохранён. Перезапустите приложение для применения изменений."),
                bgcolor=ft.Colors.GREEN,
            ))
        except Exception as ex:
            self.page.show_dialog(ft.SnackBar(ft.Text(f"Ошибка сохранения: {ex}"), bgcolor=ft.Colors.RED))
