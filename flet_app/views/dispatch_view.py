import flet as ft
from data import (
    get_all_products, get_product_available_quantity,
    get_product_components, get_product_by_id,
    dispatch_product, dispatch_products_batch,
    get_all_discs, get_all_boxes,
    write_off_component, get_stock_disc_quantity, get_stock_box_quantity,
)
from datetime import date, datetime


class DispatchView:
    def __init__(self, app):
        self.app = app
        self.page = app.page
        self.batch_table = None
        self.single_dd = None
        self.single_qty = None
        self.single_date = None
        self.tab_index = 0

    @staticmethod
    def _parse_disp_date(val):
        v = val.strip() if val else ""
        if not v:
            return None
        parts = v.split(".")
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
        return v

    def refresh(self):
        pass

    def build(self):
        header = ft.Text("Списание комплектов", size=24, weight=ft.FontWeight.BOLD)
        return ft.Column([header, ft.Divider(), self._build_tabs()], expand=True, scroll=ft.ScrollMode.AUTO)

    def _build_tabs(self):
        tab_names = ["Пакетное списание", "Списание одного ИК", "Списание по браку"]
        tab_buttons = ft.Row(
            [ft.FilledTonalButton(
                n,
                on_click=lambda e, i=i: self._switch_tab(i),
            ) for i, n in enumerate(tab_names)],
            spacing=5,
        )

        self.content_stack = ft.Stack([
            self._build_batch_tab(),
            self._build_single_tab(),
            self._build_writeoff_tab(),
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

    def _build_date_field(self, label, initial_value=None):
        if initial_value is None:
            initial_value = date.today().strftime("%d.%m.%Y")
        field = ft.TextField(label=label, value=initial_value, width=200)

        def on_date_selected(ev):
            val = ev.data
            if isinstance(val, datetime):
                field.value = val.astimezone().strftime("%d.%m.%Y")
            elif isinstance(val, date):
                field.value = val.strftime("%d.%m.%Y")
            elif isinstance(val, str) and len(val) >= 10:
                field.value = val[8:10] + "." + val[5:7] + "." + val[:4]
            else:
                try:
                    val = ev.control.value
                    if isinstance(val, datetime):
                        field.value = val.astimezone().strftime("%d.%m.%Y")
                    elif isinstance(val, date):
                        field.value = val.strftime("%d.%m.%Y")
                    elif isinstance(val, str) and len(val) >= 10:
                        field.value = val[8:10] + "." + val[5:7] + "." + val[:4]
                except Exception:
                    pass
            self.page.update()

        picker = ft.DatePicker(
            on_change=on_date_selected,
            locale=ft.Locale("ru"),
        )

        def open_picker(e):
            try:
                parts = field.value.split(".")
                if len(parts) == 3:
                    picker.value = date(int(parts[2]), int(parts[1]), int(parts[0]))
                else:
                    picker.value = date.today()
            except (ValueError, TypeError, IndexError):
                picker.value = date.today()
            self.page.show_dialog(picker)

        btn = ft.IconButton(
            ft.Icons.CALENDAR_MONTH,
            tooltip="Выбрать дату",
            on_click=open_picker,
        )
        return ft.Row([field, btn], spacing=5)

    def _build_batch_tab(self):
        date_row = self._build_date_field("Дата отгрузки (ДД.ММ.ГГГГ)")
        self.batch_date_field = date_row.controls[0]
        self.batch_date_row = date_row

        self.batch_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Продукт")),
                ft.DataColumn(ft.Text("Доступно")),
                ft.DataColumn(ft.Text("Списать")),
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
        self.load_batch_table()

        btn_row = ft.Row([
            ft.FilledButton("Списать отмеченные", icon=ft.Icons.OUTBOUND, on_click=self.execute_batch_dispatch),
        ])

        return ft.Column([
            ft.Text("Укажите количество для списания по каждому продукту:", italic=True),
            self.batch_date_row,
            ft.Divider(height=5),
            self.batch_table,
            btn_row,
        ], expand=True, scroll=ft.ScrollMode.AUTO)

    def load_batch_table(self):
        products = get_all_products()
        rows = []
        self.batch_qty_fields = {}
        for p in products:
            available = get_product_available_quantity(p.doc_id)
            qty_field = ft.TextField(value="0", width=80, text_align=ft.TextAlign.RIGHT, keyboard_type=ft.KeyboardType.NUMBER)
            self.batch_qty_fields[p.doc_id] = qty_field
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(p.doc_id))),
                ft.DataCell(ft.Text(p.get('name', ''))),
                ft.DataCell(ft.Text(str(available))),
                ft.DataCell(qty_field),
            ]))
        self.batch_table.rows = rows or [ft.DataRow(cells=[ft.DataCell(ft.Text("Нет продуктов")) for _ in range(4)])]

    def execute_batch_dispatch(self, e):
        items = []
        for p in get_all_products():
            try:
                qty = int(self.batch_qty_fields[p.doc_id].value)
                if qty > 0:
                    items.append((p.doc_id, qty))
            except (ValueError, TypeError):
                pass

        if not items:
            self.page.show_dialog(ft.SnackBar(ft.Text("Укажите количество для списания хотя бы по одному продукту"), bgcolor=ft.Colors.ORANGE))
            return

        dt = self._parse_disp_date(self.batch_date_field.value.strip())
        success, messages = dispatch_products_batch(items, dt)
        if success:
            for msg in messages:
                self.page.show_dialog(ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN))
        else:
            for msg in messages:
                self.page.show_dialog(ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.RED))
        self.load_batch_table()
        self.page.update()

    def _build_single_tab(self):
        products = get_all_products()
        options = [ft.dropdown.Option(str(p.doc_id), f"{p['name']} (ID:{p.doc_id})") for p in products]
        self.single_dd = ft.Dropdown(label="Выберите продукт", options=options, width=400)
        self.single_qty = ft.TextField(label="Количество", value="1", width=120, text_align=ft.TextAlign.RIGHT, keyboard_type=ft.KeyboardType.NUMBER)
        single_date_row = self._build_date_field("Дата (ДД.ММ.ГГГГ)")
        self.single_date = single_date_row.controls[0]

        info_btn = ft.FilledButton("Показать состав", on_click=self.show_single_components)

        dispatch_btn = ft.FilledButton("Списать ИК", icon=ft.Icons.OUTBOUND, on_click=self.execute_single_dispatch)

        return ft.Column([
            ft.Text("Списание одного продукта с указанием даты:", italic=True),
            ft.Divider(),
            self.single_dd,
            ft.Row([self.single_qty, single_date_row], spacing=10),
            ft.Row([info_btn, dispatch_btn], spacing=10),
        ], expand=True, scroll=ft.ScrollMode.AUTO)

    def show_single_components(self, e):
        if not self.single_dd.value:
            self.page.show_dialog(ft.SnackBar(ft.Text("Сначала выберите продукт"), bgcolor=ft.Colors.ORANGE))
            return
        product_id = int(self.single_dd.value)
        product = get_product_by_id(product_id)
        components = get_product_components(product_id)
        discs = {d.doc_id: d['name'] for d in get_all_discs()}
        boxes = {b.doc_id: b['name'] for b in get_all_boxes()}

        rows = []
        for c in components:
            disc_name = discs.get(c.get('disc_id'), '—')
            box_name = boxes.get(c.get('box_id'), '—')
            rows.append(f"• {disc_name} x{c.get('disc_quantity', 0)}, {box_name} x{c.get('box_quantity', 0)}")

        content = "\n".join(rows) if rows else "Нет компонентов"
        dlg = ft.AlertDialog(
            title=ft.Text(f"Состав: {product['name']}"),
            content=ft.Text(content),
            actions=[ft.TextButton("Закрыть", on_click=lambda e: self.close_dialog(dlg))],
        )
        self.page.show_dialog(dlg)

    def execute_single_dispatch(self, e):
        if not self.single_dd.value:
            self.page.show_dialog(ft.SnackBar(ft.Text("Выберите продукт"), bgcolor=ft.Colors.ORANGE))
            return
        try:
            product_id = int(self.single_dd.value)
            qty = int(self.single_qty.value)
            dt = self._parse_disp_date(self.single_date.value.strip())
            success, msg = dispatch_product(product_id, qty, dt)
            if success:
                self.page.show_dialog(ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN))
            else:
                self.page.show_dialog(ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.RED))
        except (ValueError, TypeError) as ex:
            self.page.show_dialog(ft.SnackBar(ft.Text(f"Ошибка: {ex}"), bgcolor=ft.Colors.RED))
        self.page.update()

    def _build_writeoff_tab(self):
        all_discs = get_all_discs()
        all_boxes = get_all_boxes()

        self.writeoff_type = ft.Dropdown(
            label="Тип",
            options=[
                ft.dropdown.Option("disc", "Носитель"),
                ft.dropdown.Option("box", "Коробка"),
            ],
            value="disc",
            width=150,
        )

        disc_options = [ft.dropdown.Option(str(d.doc_id), d['name']) for d in all_discs]
        box_options = [ft.dropdown.Option(str(b.doc_id), b['name']) for b in all_boxes]

        self.writeoff_item = ft.Dropdown(
            label="Элемент",
            options=disc_options,
            width=300,
        )

        disc_stock = {s['disc_id']: s['quantity'] for s in self._get_stock_dict('disc')}
        box_stock = {s['box_id']: s['quantity'] for s in self._get_stock_dict('box')}
        self.writeoff_stock_text = ft.Text("", size=12, color=ft.Colors.GREY)

        def update_stock_info(e=None):
            if self.writeoff_item.value:
                cid = int(self.writeoff_item.value)
                if self.writeoff_type.value == 'disc':
                    qty = disc_stock.get(cid, 0)
                else:
                    qty = box_stock.get(cid, 0)
                self.writeoff_stock_text.value = f"На складе: {qty} шт."
            else:
                self.writeoff_stock_text.value = ""
            self.page.update()

        self.writeoff_item.on_change = update_stock_info
        self.writeoff_qty = ft.TextField(label="Количество", value="1", width=120, text_align=ft.TextAlign.RIGHT, keyboard_type=ft.KeyboardType.NUMBER)
        self.writeoff_reason = ft.TextField(label="Причина", width=400)

        def on_type_change(e):
            self.writeoff_item.options = box_options if self.writeoff_type.value == 'box' else disc_options
            self.writeoff_item.value = None
            self.writeoff_stock_text.value = ""
            self.page.update()

        self.writeoff_type.on_change = on_type_change

        execute_btn = ft.FilledButton("Списать по браку", icon=ft.Icons.BLOCK, on_click=self.execute_writeoff)

        return ft.Column([
            ft.Text("Списание компонентов по браку:", italic=True),
            ft.Divider(),
            ft.Row([self.writeoff_type, self.writeoff_item], spacing=10),
            self.writeoff_stock_text,
            ft.Row([self.writeoff_qty, self.writeoff_reason], spacing=10),
            execute_btn,
        ], expand=True, scroll=ft.ScrollMode.AUTO)

    def _get_stock_dict(self, component_type):
        if component_type == 'disc':
            from data import get_all_stock_discs
            return get_all_stock_discs()
        else:
            from data import get_all_stock_boxes
            return get_all_stock_boxes()

    def execute_writeoff(self, e):
        if not self.writeoff_item.value:
            self.page.show_dialog(ft.SnackBar(ft.Text("Выберите элемент"), bgcolor=ft.Colors.ORANGE))
            return
        try:
            cid = int(self.writeoff_item.value)
            qty = int(self.writeoff_qty.value)
            reason = self.writeoff_reason.value
            success, msg = write_off_component(self.writeoff_type.value, cid, qty, reason)
            if success:
                self.page.show_dialog(ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN))
            else:
                self.page.show_dialog(ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.RED))
        except (ValueError, TypeError) as ex:
            self.page.show_dialog(ft.SnackBar(ft.Text(f"Ошибка: {ex}"), bgcolor=ft.Colors.RED))
        self.page.update()

    def close_dialog(self, dlg):
        self.page.pop_dialog()
