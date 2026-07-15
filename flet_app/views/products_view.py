import flet as ft
from data import (
    get_all_products, add_product, update_product, delete_product,
    get_product_components, get_product_available_quantity,
    get_all_discs, get_all_boxes,
    add_product_with_components, update_product_with_components,
)


class ProductsView:
    def __init__(self, app):
        self.app = app
        self.page = app.page
        self.products_table = None
        self.filter_text = ""

    def refresh(self):
        pass

    def build(self):
        header = ft.Text("Комплектация продуктов", size=24, weight=ft.FontWeight.BOLD)

        search_row = ft.Row([
            ft.TextField(
                hint_text="Поиск по названию...",
                expand=True,
                on_change=self.on_search,
            ),
            ft.FilledButton(
                "Добавить продукт",
                icon=ft.Icons.ADD,
                on_click=self.open_add_dialog,
            ),
        ])

        self.products_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Название")),
                ft.DataColumn(ft.Text("Описание")),
                ft.DataColumn(ft.Text("Доступно")),
                ft.DataColumn(ft.Text("Действия")),
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
            sort_column_index=0,
        )

        self.load_products()

        return ft.Column([header, search_row, ft.Divider(), self.products_table], expand=True, scroll=ft.ScrollMode.AUTO)

    def on_search(self, e):
        self.filter_text = e.control.value.lower()
        self.load_products()

    def load_products(self):
        products = get_all_products()
        if self.filter_text:
            products = [p for p in products if self.filter_text in p.get('name', '').lower()]

        rows = []
        for p in products:
            available = get_product_available_quantity(p.doc_id)
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(p.get('name', ''))),
                        ft.DataCell(ft.Text(p.get('description', ''))),
                        ft.DataCell(ft.Text(str(available))),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.Icons.VISIBILITY, tooltip="Состав", on_click=lambda e, pid=p.doc_id: self.show_components(pid)),
                                ft.IconButton(ft.Icons.EDIT, tooltip="Редактировать", on_click=lambda e, pid=p.doc_id: self.open_edit_dialog(pid)),
                                ft.IconButton(ft.Icons.DELETE, tooltip="Удалить", on_click=lambda e, pid=p.doc_id: self.confirm_delete(pid)),
                            ])
                        ),
                    ]
                )
            )

        if rows:
            self.products_table.rows = rows
        else:
            self.products_table.rows = [
                ft.DataRow(cells=[ft.DataCell(ft.Text("Нет данных")) for _ in range(4)])
            ]
        self.page.update()

    def show_components(self, product_id):
        product = get_all_products()
        product = next((p for p in product if p.doc_id == product_id), None)
        components = get_product_components(product_id)

        discs = {d.doc_id: d['name'] for d in get_all_discs()}
        boxes = {b.doc_id: b['name'] for b in get_all_boxes()}

        rows = []
        for c in components:
            disc_name = discs.get(c.get('disc_id'), '—')
            box_name = boxes.get(c.get('box_id'), '—')
            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(disc_name)),
                    ft.DataCell(ft.Text(str(c.get('disc_quantity', 0)))),
                    ft.DataCell(ft.Text(box_name)),
                    ft.DataCell(ft.Text(str(c.get('box_quantity', 0)))),
                ])
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Носитель")),
                ft.DataColumn(ft.Text("Кол-во")),
                ft.DataColumn(ft.Text("Коробка")),
                ft.DataColumn(ft.Text("Кол-во")),
            ],
            rows=rows or [ft.DataRow(cells=[ft.DataCell(ft.Text("Нет компонентов")) for _ in range(4)])],
        )

        dlg = ft.AlertDialog(
            title=ft.Text(f"Состав: {product['name'] if product else ''}"),
            content=ft.Column([table], scroll=ft.ScrollMode.AUTO, width=500),
            actions=[ft.TextButton("Закрыть", on_click=lambda e: self.close_dialog(dlg))],
        )
        self.page.show_dialog(dlg)

    def open_add_dialog(self, e):
        self._open_product_dialog()

    def open_edit_dialog(self, product_id):
        product = next((p for p in get_all_products() if p.doc_id == product_id), None)
        if product:
            self._open_product_dialog(product)

    def _open_product_dialog(self, product=None):
        is_edit = product is not None
        name_field = ft.TextField(label="Название", value=product['name'] if is_edit else "", expand=True)
        code_field = ft.TextField(label="Код", value=product.get('code', '') if is_edit else "", expand=True)
        desc_field = ft.TextField(label="Описание", value=product.get('description', '') if is_edit else "", expand=True, multiline=True, min_lines=2)

        all_discs = get_all_discs()
        all_boxes = get_all_boxes()

        existing_components = get_product_components(product.doc_id) if is_edit else []

        components_list = ft.Column(scroll=ft.ScrollMode.AUTO, height=200)

        def build_component_rows():
            rows = []
            for i, comp in enumerate(existing_components):
                disc_dd = ft.Dropdown(
                    label="Носитель",
                    options=[ft.dropdown.Option(str(d.doc_id), d['name']) for d in all_discs],
                    value=str(comp.get('disc_id')) if comp.get('disc_id') else None,
                    width=180,
                )
                disc_qty = ft.TextField(label="Кол-во", value=str(comp.get('disc_quantity', 0)), width=80, text_align=ft.TextAlign.RIGHT)
                box_dd = ft.Dropdown(
                    label="Коробка",
                    options=[ft.dropdown.Option(str(b.doc_id), b['name']) for b in all_boxes],
                    value=str(comp.get('box_id')) if comp.get('box_id') else None,
                    width=180,
                )
                box_qty = ft.TextField(label="Кол-во", value=str(comp.get('box_quantity', 0)), width=80, text_align=ft.TextAlign.RIGHT)
                remove_btn = ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color=ft.Colors.RED, tooltip="Удалить")

                comp_row = ft.Row([disc_dd, disc_qty, box_dd, box_qty, remove_btn], spacing=5)
                components_list.controls.append(comp_row)

                remove_btn.on_click = lambda e, row=comp_row: (
                    components_list.controls.remove(row),
                    self.page.update()
                )

            if not components_list.controls:
                comp_row = self._empty_component_row(components_list, all_discs, all_boxes)
                components_list.controls.append(comp_row)

        def add_component_row(e):
            comp_row = self._empty_component_row(components_list, all_discs, all_boxes)
            components_list.controls.append(comp_row)
            self.page.update()

        build_component_rows()

        dlg = ft.AlertDialog(
            title=ft.Text("Редактирование продукта" if is_edit else "Новый продукт"),
            content=ft.Column([
                name_field,
                code_field,
                desc_field,
                ft.Text("Состав комплекта:", weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Text("Носитель", weight=ft.FontWeight.W_500, width=180),
                    ft.Text("Кол-во", weight=ft.FontWeight.W_500, width=80),
                    ft.Text("Коробка", weight=ft.FontWeight.W_500, width=180),
                    ft.Text("Кол-во", weight=ft.FontWeight.W_500, width=80),
                ], spacing=5),
                components_list,
                ft.FilledButton("+ Добавить компонент", icon=ft.Icons.ADD, on_click=add_component_row),
            ], width=600, height=500, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close_dialog(dlg)),
                ft.FilledButton("Сохранить", on_click=lambda e: self._save_product(
                    dlg, product.doc_id if is_edit else None,
                    name_field, code_field, desc_field,
                    components_list
                )),
            ],
        )
        self.page.show_dialog(dlg)

    def _empty_component_row(self, components_list, all_discs, all_boxes):
        disc_dd = ft.Dropdown(
            label="Носитель",
            options=[ft.dropdown.Option(str(d.doc_id), d['name']) for d in all_discs],
            width=180,
        )
        disc_qty = ft.TextField(label="Кол-во", value="0", width=80, text_align=ft.TextAlign.RIGHT)
        box_dd = ft.Dropdown(
            label="Коробка",
            options=[ft.dropdown.Option(str(b.doc_id), b['name']) for b in all_boxes],
            width=180,
        )
        box_qty = ft.TextField(label="Кол-во", value="0", width=80, text_align=ft.TextAlign.RIGHT)
        remove_btn = ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color=ft.Colors.RED, tooltip="Удалить")

        comp_row = ft.Row([disc_dd, disc_qty, box_dd, box_qty, remove_btn], spacing=5)
        remove_btn.on_click = lambda e: (
            components_list.controls.remove(comp_row),
            self.page.update()
        )
        return comp_row

    def _save_product(self, dlg, product_id, name_field, code_field, desc_field, components_list):
        name = name_field.value.strip()
        if not name:
            name_field.error_text = "Название обязательно"
            self.page.update()
            return

        components = []
        for row in components_list.controls:
            if isinstance(row, ft.Row) and len(row.controls) >= 4:
                disc_id = int(row.controls[0].value) if row.controls[0].value else None
                disc_qty = int(row.controls[1].value or 0)
                box_id = int(row.controls[2].value) if row.controls[2].value else None
                box_qty = int(row.controls[3].value or 0)
                if disc_id or box_id:
                    components.append({
                        'disc_id': disc_id,
                        'disc_quantity': disc_qty,
                        'box_id': box_id,
                        'box_quantity': box_qty,
                    })

        try:
            if product_id:
                update_product_with_components(product_id, name, code_field.value, desc_field.value, components)
            else:
                add_product_with_components(name, code_field.value, desc_field.value, components)
            self.close_dialog(dlg)
            self.load_products()
        except Exception as ex:
            self.page.show_dialog(ft.SnackBar(ft.Text(f"Ошибка: {ex}"), bgcolor=ft.Colors.RED))

    def confirm_delete(self, product_id):
        product = next((p for p in get_all_products() if p.doc_id == product_id), None)
        dlg = ft.AlertDialog(
            title=ft.Text("Подтверждение удаления"),
            content=ft.Text(f"Удалить продукт «{product['name']}» и его состав?"),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.close_dialog(dlg)),
                ft.FilledButton("Удалить", on_click=lambda e: (
                    delete_product(product_id),
                    self.close_dialog(dlg),
                    self.load_products()
                )),
            ],
        )
        self.page.show_dialog(dlg)

    def close_dialog(self, dlg):
        self.page.pop_dialog()
