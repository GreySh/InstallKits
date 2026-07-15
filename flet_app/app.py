import flet as ft
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flet_app.views.products_view import ProductsView
from flet_app.views.stock_view import StockView
from flet_app.views.dispatch_view import DispatchView
from flet_app.views.operations_view import OperationsView
from flet_app.views.settings_view import SettingsView
from flet_app.views.report_view import ReportDialog
from settings_manager import get_setting, set_setting


class InstallKitsApp:
    def __init__(self, page: ft.Page):
        self.page = page
        page.title = "InstallKits — Учёт инсталляционных комплектов"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window.min_width = 900
        page.window.min_height = 600

        self.views = {}
        self.current_index = 0

        self._restore_window_geometry()
        self._setup_window_handlers()

    def _restore_window_geometry(self):
        w = get_setting("window_width")
        h = get_setting("window_height")
        self.page.window.width = w if isinstance(w, (int, float)) else 1200
        self.page.window.height = h if isinstance(h, (int, float)) else 800
        left = get_setting("window_left")
        top = get_setting("window_top")
        if isinstance(left, (int, float)):
            self.page.window.left = left
        if isinstance(top, (int, float)):
            self.page.window.top = top

    def _save_window_geometry(self):
        w = getattr(self.page.window, "width", None)
        h = getattr(self.page.window, "height", None)
        left = getattr(self.page.window, "left", None)
        top = getattr(self.page.window, "top", None)
        if w:
            set_setting("window_width", w)
        if h:
            set_setting("window_height", h)
        if left is not None:
            set_setting("window_left", left)
        if top is not None:
            set_setting("window_top", top)

    def _on_window_event(self, e):
        if e.type in (ft.WindowEventType.RESIZED, ft.WindowEventType.MOVED, ft.WindowEventType.CLOSE):
            self._save_window_geometry()

    def _setup_window_handlers(self):
        self.page.window.on_event = self._on_window_event

        self.nav_rail = ft.NavigationRail(
            expand=True,
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=160,
            min_extended_width=180,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.INVENTORY_2,
                    selected_icon=ft.Icons.INVENTORY,
                    label="Комплектация",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.WAREHOUSE,
                    selected_icon=ft.Icons.WAREHOUSE_OUTLINED,
                    label="Остатки",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.OUTBOUND,
                    selected_icon=ft.Icons.OUTBOUND_OUTLINED,
                    label="Списание",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.HISTORY,
                    selected_icon=ft.Icons.HISTORY_OUTLINED,
                    label="История",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS,
                    selected_icon=ft.Icons.SETTINGS_OUTLINED,
                    label="Настройки",
                ),
            ],
            on_change=self.on_nav_change,
        )

        self.content_area = ft.Container(
            expand=True,
            padding=20,
        )

        nav_column = ft.Column([
            self.nav_rail,
            ft.Container(
                content=ft.FilledButton(
                    "Отчеты",
                    icon=ft.Icons.ASSESSMENT,
                    on_click=lambda e: ReportDialog(self.page).open(),
                ),
                padding=ft.Padding(left=10, right=10, bottom=10),
            ),
        ], width=180, spacing=0)

        self.page.add(
            ft.Row(
                [nav_column, ft.VerticalDivider(width=1), self.content_area],
                expand=True,
                spacing=0,
            )
        )

        self.views[0] = ProductsView(self)
        self.views[1] = StockView(self)
        self.views[2] = DispatchView(self)
        self.views[3] = OperationsView(self)
        self.views[4] = SettingsView(self)

        self.show_view(0)

    def on_nav_change(self, e):
        self.show_view(e.control.selected_index)

    def show_view(self, index):
        self.current_index = index
        self.nav_rail.selected_index = index
        if index in self.views:
            view = self.views[index]
            view.refresh()
            self.content_area.content = view.build()
        self.page.update()


def main():
    ft.run(InstallKitsApp)


if __name__ == "__main__":
    main()
