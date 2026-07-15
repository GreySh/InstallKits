import flet as ft
from data import (
    get_all_discs, get_all_boxes,
    get_all_stock_discs, get_all_stock_boxes,
    get_all_products, get_product_components,
    get_stock_disc_quantity, get_stock_box_quantity,
    adjust_stock_disc, adjust_stock_box,
    add_stock_disc, add_stock_box,
    get_product_available_quantity,
    add_disc, add_box,
)


class StockView:
    def __init__(self, app):
        self.app = app
        self.page = app.page
        self.tab_index = 0
        self.discs_table = None
        self.boxes_table = None
        self.kits_table = None

    def refresh(self):
        pass

    def build(self):
        header = ft.Text("Остатки на складе", size=24, weight=ft.FontWeight.BOLD)
        return ft.Column([header, ft.Divider(), self._build_tabs()], expand=True, scroll=ft.ScrollMode.AUTO)

    def _build_tabs(self):
        tab_names = ["Носители", "Коробки", "Комплекты"]
        tab_buttons = ft.Row(
            [ft.FilledTonalButton(
                n,
                on_click=lambda e, i=i: self._switch_tab(i),
            ) for i, n in enumerate(tab_names)],
            spacing=5,
        )

        self.content_stack = ft.Stack([
            self._build_discs_tab(),
            self._build_boxes_tab(),
            self._build_kits_tab(),
        ])
        self._update_tab_visibility()

        return ft.Column([tab_buttons, ft.Divider(height=5), self.content_stack], expand=True)

    def _switch_tab(self, index):
        self.tab_index = index
        self._update_tab_visibility()

    def _update_tab_visibility(self):
        for i, control in enumerate(self.content_stack.controls):
            control.visible = (i == self.tab_index)
        if self.page:
            self.page.update()

    def _build_discs_tab(self):
        discs_header = ft.Row([
            ft.Text("Носители:", size=18, weight=ft.FontWeight.BOLD),
            ft.FilledButton("Приход", icon=ft.Icons.ADD_CIRCLE, on_click=lambda e: self.open_add_stock_dialog('disc')),
            ft.FilledButton("Корректировка", icon=ft.Icons.TUNE, on_click=lambda e: self.open_adjust_stock_dialog('disc')),
            ft.FilledButton("Новый носитель", icon=ft.Icons.ADD, on_click=lambda e: self.open_new_component_dialog('disc')),
        ], spacing=10)

        self.discs_table = self._build_stock_table()
        self._load_discs()

        return ft.Column([discs_header, self.discs_table], expand=True, scroll=ft.ScrollMode.AUTO)

    def _build_boxes_tab(self):
        boxes_header = ft.Row([
            ft.Text("Коробки:", size=18, weight=ft.FontWeight.BOLD),
            ft.FilledButton("Приход", icon=ft.Icons.ADD_CIRCLE, on_click=lambda e: self.open_add_stock_dialog('box')),
            ft.FilledButton("Корректировка", icon=ft.Icons.TUNE, on_click=lambda e: self.open_adjust_stock_dialog('box')),
            ft.FilledButton("Новая коробка", icon=ft.Icons.ADD, on_click=lambda e: self.open_new_component_dialog('box')),
        ], spacing=10)

        self.boxes_table = self._build_stock_table()
        self._load_boxes()

        return ft.Column([boxes_header, self.boxes_table], expand=True, scroll=ft.ScrollMode.AUTO)

    def _build_kits_tab(self):
        kits_header = ft.Text("Доступные комплекты:", size=18, weight=ft.FontWeight.BOLD)

        self.kits_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Название")),
                ft.DataColumn(ft.Text("Доступно комплектов")),
            ],
            rows=[],
            border=ft.border.Border(
                left=ft.BorderSide(1, ft.Colors.OUTLINE),
                top=ft.BorderSide(1, ft.Colors.OUTLINE),
                right=ft.BorderSide(1, ft.Colors.OUTLINE),
                bottom=ft.BorderSide(1, ft.Colors.OUTLINE),
            ),
            border_radius=8,
            vertical_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        )
        self._load_kits()

        return ft.Column([kits_header, self.kits_table], expand=True, scroll=ft.ScrollMode.AUTO)

    def _build_stock_table(self):
        columns = [
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Название")),
            ft.DataColumn(ft.Text("Количество")),
            ft.DataColumn(ft.Text("Действия")),
        ]
        return ft.DataTable(columns=columns, rows=[], border=ft.border.Border(
            left=ft.BorderSide(1, ft.Colors.OUTLINE),
            top=ft.BorderSide(1, ft.Colors.OUTLINE),
            right=ft.BorderSide(1, ft.Colors.OUTLINE),
            bottom=ft.BorderSide(1, ft.Colors.OUTLINE),
        ), border_radius=8, vertical_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT))

    def load_stock(self):
        self._load_discs()
        self._load_boxes()
        self._load_kits()
        if self.page:
            self.page.update()

    def _load_discs(self):
        discs = get_all_stock_discs()
        rows = []
        for d in discs:
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(d['disc_id']))),
                ft.DataCell(ft.Text(d['disc_name'])),
                ft.DataCell(ft.Text(str(d['quantity']))),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, tooltip="Приход", on_click=lambda e, did=d['disc_id']: self.open_add_stock_dialog('disc', did)),
                    ft.IconButton(ft.Icons.TUNE, tooltip="Корректировка", on_click=lambda e, did=d['disc_id']: self.open_adjust_stock_dialog('disc', did)),
                ])),
            ]))
        self.discs_table.rows = rows or [ft.DataRow(cells=[ft.DataCell(ft.Text("Нет данных")) for _ in range(4)])]

    def _load_boxes(self):
        boxes = get_all_stock_boxes()
        rows = []
        for b in boxes:
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(b['box_id']))),
                ft.DataCell(ft.Text(b['box_name'])),
                ft.DataCell(ft.Text(str(b['quantity']))),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, tooltip="Приход", on_click=lambda e, bid=b['box_id']: self.open_add_stock_dialog('box', bid)),
                    ft.IconButton(ft.Icons.TUNE, tooltip="Корректировка", on_click=lambda e, bid=b['box_id']: self.open_adjust_stock_dialog('box', bid)),
                ])),
            ]))
        self.boxes_table.rows = rows or [ft.DataRow(cells=[ft.DataCell(ft.Text("Нет данных")) for _ in range(4)])]

    def _load_kits(self):
        products = get_all_products()
        rows = []
        for p in products:
            available = get_product_available_quantity(p.doc_id)
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(p.get('name', ''))),
                ft.DataCell(ft.Text(str(available))),
            ]))
        self.kits_table.rows = rows or [ft.DataRow(cells=[ft.DataCell(ft.Text("Нет продуктов")) for _ in range(2)])]

    def open_new_component_dialog(self, component_type):
        name_field = ft.TextField(label="Название", expand=True)
        desc_field = ft.TextField(label="Описание", expand=True)
        label = "носителя" if component_type == 'disc' else "коробки"

        dlg = ft.AlertDialog(
            title=ft.Text(f"Новый {label}"),
            content=ft.Column([name_field, desc_field], width=400),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close_dialog(dlg)),
                ft.FilledButton("Создать", on_click=lambda e: self._save_new_component(dlg, component_type, name_field, desc_field)),
            ],
        )
        self.page.show_dialog(dlg)

    def _save_new_component(self, dlg, component_type, name_field, desc_field):
        name = name_field.value.strip()
        if not name:
            name_field.error_text = "Название обязательно"
            self.page.update()
            return
        try:
            if component_type == 'disc':
                add_disc(name, 0, desc_field.value)
            else:
                add_box(name, 0, desc_field.value)
            self.close_dialog(dlg)
            self.load_stock()
        except Exception as ex:
            self.page.show_dialog(ft.SnackBar(ft.Text(f"Ошибка: {ex}"), bgcolor=ft.Colors.RED))

    def open_add_stock_dialog(self, component_type, component_id=None):
        if component_type == 'disc':
            all_items = get_all_discs()
            existing = get_all_stock_discs()
        else:
            all_items = get_all_boxes()
            existing = get_all_stock_boxes()

        existing_ids = {s['disc_id' if component_type == 'disc' else 'box_id'] for s in existing}

        options = [ft.dropdown.Option(str(d.doc_id), d['name']) for d in all_items if d.doc_id in existing_ids]
        dd = ft.Dropdown(
            label="Выберите" + (" носитель" if component_type == 'disc' else " коробку"),
            options=options,
            value=str(component_id) if component_id else None,
            width=300,
        )
        qty_field = ft.TextField(label="Количество", value="1", width=150, text_align=ft.TextAlign.RIGHT, keyboard_type=ft.KeyboardType.NUMBER)

        label = "дисков" if component_type == 'disc' else "коробок"

        dlg = ft.AlertDialog(
            title=ft.Text(f"Приход {label}"),
            content=ft.Column([dd, qty_field], width=400),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close_dialog(dlg)),
                ft.FilledButton("Провести", on_click=lambda e: self._execute_add_stock(dlg, component_type, dd, qty_field)),
            ],
        )
        self.page.show_dialog(dlg)

    def _execute_add_stock(self, dlg, component_type, dd, qty_field):
        try:
            cid = int(dd.value)
            qty = int(qty_field.value)
            if qty <= 0:
                raise ValueError("Количество должно быть положительным")
            if component_type == 'disc':
                add_stock_disc(cid, qty)
            else:
                add_stock_box(cid, qty)
            self.close_dialog(dlg)
            self.load_stock()
        except (ValueError, TypeError) as ex:
            self.page.show_dialog(ft.SnackBar(ft.Text(f"Ошибка: {ex}"), bgcolor=ft.Colors.RED))

    def open_adjust_stock_dialog(self, component_type, component_id=None):
        if component_type == 'disc':
            all_items = get_all_discs()
            existing = get_all_stock_discs()
        else:
            all_items = get_all_boxes()
            existing = get_all_stock_boxes()

        existing_ids = {s['disc_id' if component_type == 'disc' else 'box_id'] for s in existing}
        options = [ft.dropdown.Option(str(d.doc_id), d['name']) for d in all_items if d.doc_id in existing_ids]
        dd = ft.Dropdown(
            label="Выберите" + (" носитель" if component_type == 'disc' else " коробку"),
            options=options,
            value=str(component_id) if component_id else None,
            width=300,
        )
        qty_field = ft.TextField(label="Новое количество", value="0", width=150, text_align=ft.TextAlign.RIGHT, keyboard_type=ft.KeyboardType.NUMBER)

        label = "носителя" if component_type == 'disc' else "коробки"

        dlg = ft.AlertDialog(
            title=ft.Text(f"Корректировка {label}"),
            content=ft.Column([dd, qty_field], width=400),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close_dialog(dlg)),
                ft.FilledButton("Установить", on_click=lambda e: self._execute_adjust_stock(dlg, component_type, dd, qty_field)),
            ],
        )
        self.page.show_dialog(dlg)

    def _execute_adjust_stock(self, dlg, component_type, dd, qty_field):
        try:
            cid = int(dd.value)
            qty = int(qty_field.value)
            if qty < 0:
                raise ValueError("Количество не может быть отрицательным")
            if component_type == 'disc':
                adjust_stock_disc(cid, qty, 'set')
            else:
                adjust_stock_box(cid, qty, 'set')
            self.close_dialog(dlg)
            self.load_stock()
        except (ValueError, TypeError) as ex:
            self.page.show_dialog(ft.SnackBar(ft.Text(f"Ошибка: {ex}"), bgcolor=ft.Colors.RED))

    def close_dialog(self, dlg):
        self.page.pop_dialog()
