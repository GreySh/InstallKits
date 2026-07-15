"""
Диалоговые окна Toga для InstallKits.
"""

import types

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from data import (
    add_disc, add_box,
    add_product_with_components, update_product_with_components,
    get_all_discs, get_all_boxes, get_disc_by_id, get_box_by_id,
    adjust_stock_disc, adjust_stock_box, update_disc, update_box,
    get_product_by_id, get_product_components,
    write_off_component, dispatch_product,
)


# ─── Сохранение геометрии окон ──────────────────────────────

WINDOW_GEOMETRIES = {}


def load_geometries():
    global WINDOW_GEOMETRIES
    try:
        from settings_manager import SETTINGS_FILE
        import os
        import json
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'window_geometries' in data:
                    WINDOW_GEOMETRIES.update(data['window_geometries'])
    except Exception:
        pass


def save_geometry(name, size, position):
    try:
        from settings_manager import SETTINGS_FILE
        import os
        import json
        w = int(size[0]) if size else 0
        h = int(size[1]) if size else 0
        x = int(position[0]) if position else 0
        y = int(position[1]) if position else 0
        WINDOW_GEOMETRIES[name] = {'width': w, 'height': h, 'x': x, 'y': y}
        current = {}
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                current = json.load(f)
        current['window_geometries'] = WINDOW_GEOMETRIES
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _rect_on_screen(x, y, w, h):
    """Возвращает True, если прямоугольник окна видим хотя бы на одном мониторе."""
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        rect = wintypes.RECT(int(x), int(y), int(x + w), int(y + h))
        MONITOR_DEFAULTTONULL = 0
        hmon = user32.MonitorFromRect(ctypes.byref(rect), MONITOR_DEFAULTTONULL)
        return hmon != 0
    except Exception:
        return True


def apply_geometry(window, name, default_size=None):
    load_geometries()
    geo = WINDOW_GEOMETRIES.get(name)
    applied = False
    if geo and 'width' in geo and 'x' in geo:
        w = int(geo['width'])
        h = int(geo['height'])
        try:
            window.size = (w, h)
            if _rect_on_screen(int(geo['x']), int(geo['y']), w, h):
                window.position = (int(geo['x']), int(geo['y']))
            applied = True
        except Exception:
            pass
    if not applied and default_size:
        try:
            window.size = default_size
        except Exception:
            pass
    return applied


class BaseWindow(toga.Window):
    """Базовый класс окон с сохранением геометрии."""

    geometry_name = None
    default_size = (420, 300)

    def __init__(self, **kwargs):
        default = kwargs.get("size", self.default_size)
        super().__init__(**kwargs)
        apply_geometry(self, self.geometry_name or self.__class__.__name__,
                       default)

    def close(self):
        save_geometry(self.geometry_name or self.__class__.__name__,
                     self.size, self.position)
        super().close()


def _row(*widgets, **pack):
    box = toga.Box(style=Pack(direction=ROW, margin=4, align_items="center", **pack))
    for w in widgets:
        box.add(w)
    return box


def _label(text, width=None):
    kwargs = {"style": Pack(margin=(4, 0), font_size=12)}
    if width is not None:
        kwargs["style"] = Pack(width=width, margin=(4, 0), font_size=12)
    return toga.Label(text, **kwargs)


class AddComponentWindow(BaseWindow):
    """Добавление носителя или коробки."""

    def __init__(self, comp_type, on_save=None, **kwargs):
        kwargs.setdefault("title", "Новый носитель" if comp_type == "disc" else "Новая коробка")
        kwargs.setdefault("size", (420, 260))
        super().__init__(**kwargs)
        self.comp_type = comp_type
        self.on_save = on_save
        self._build()

    def _build(self):
        box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        self.name = toga.TextInput(placeholder="Название", style=Pack(flex=1, margin=4, font_size=12))
        self.desc = toga.TextInput(placeholder="Описание", style=Pack(flex=1, margin=4, font_size=12))
        self.qty = toga.NumberInput(min=0, value=0, style=Pack(width=100, margin=4, font_size=12))
        self.error = toga.Label("", style=Pack(margin=4, color="#c0392b", font_size=12))

        box.add(_row(_label("Название:"), self.name))
        box.add(_row(_label("Описание:"), self.desc))
        box.add(_row(_label("Кол-во:"), self.qty))
        box.add(self.error)
        box.add(_row(
            toga.Button("Отмена", on_press=lambda w: self.close(), style=Pack(flex=1, margin=4, font_size=12)),
            toga.Button("Сохранить", on_press=self._save, style=Pack(flex=1, margin=4, font_size=12)),
        ))
        self.content = box

    def _save(self, widget):
        name = self.name.value.strip()
        if not name:
            self.error.text = "Введите название"
            return
        qty = int(self.qty.value or 0)
        try:
            if self.comp_type == "disc":
                add_disc(name, qty, self.desc.value.strip())
            else:
                add_box(name, qty, self.desc.value.strip())
        except ValueError as e:
            self.error.text = str(e)
            return
        if self.on_save:
            self.on_save()
        self.close()


class AdjustStockWindow(BaseWindow):
    """Корректировка остатка, добавление количества и переименование."""

    def __init__(self, comp_type, item, on_save=None, allow_rename=False,
                 fixed_op=None, **kwargs):
        if fixed_op == "add":
            title = "Добавить остаток"
        elif allow_rename:
            title = "Корректировка компонента"
        else:
            title = "Корректировка компонента"
        kwargs.setdefault("title", title)
        kwargs.setdefault("size", (460, 380 if allow_rename else 320))
        super().__init__(**kwargs)
        self.comp_type = comp_type
        self.item = item
        self.on_save = on_save
        self.allow_rename = allow_rename
        self.fixed_op = fixed_op
        self._build()

    def _build(self):
        box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        box.add(toga.Label(f"{self.item['name']}", style=Pack(margin=4, font_weight="bold", font_size=12)))
        box.add(toga.Label(f"Текущий остаток: {self.item['quantity']}",
                            style=Pack(margin=4, color="#555555", font_size=12)))

        if self.allow_rename:
            self.name = toga.TextInput(value=self.item["name"], style=Pack(flex=1, margin=4, font_size=12))
            box.add(_row(_label("Наименование:"), self.name))

        cur = get_disc_by_id(self.item["id"]) if self.comp_type == "disc" else get_box_by_id(self.item["id"])
        desc_val = cur.get("description", "") if cur else ""
        if self.fixed_op == "add":
            box.add(_row(_label("Описание:"),
                         toga.Label(desc_val or "—",
                                    style=Pack(flex=1, margin=4, font_size=12, color="#555555"))))
            self.description = None
        else:
            self.description = toga.TextInput(value=desc_val,
                                              style=Pack(flex=1, margin=4, font_size=12))
            box.add(_row(_label("Описание:"), self.description))

        if self.fixed_op == "add":
            box.add(toga.Label("Операция: добавить к текущему остатку",
                               style=Pack(margin=4, color="#555555", font_size=12)))

        default_qty = self.item["quantity"] if self.fixed_op != "add" else 0
        self.qty = toga.NumberInput(min=0, value=default_qty, style=Pack(width=120, margin=4, font_size=12))
        self.error = toga.Label("", style=Pack(margin=4, color="#c0392b", font_size=12))

        qty_label = "Приход:" if self.fixed_op == "add" else "Новый остаток:"
        box.add(_row(_label(qty_label), self.qty))
        box.add(self.error)
        box.add(_row(
            toga.Button("Отмена", on_press=lambda w: self.close(), style=Pack(flex=1, margin=4, font_size=12)),
            toga.Button("Применить", on_press=self._apply, style=Pack(flex=1, margin=4, font_size=12)),
        ))
        self.content = box

    def _save_meta(self):
        if self.comp_type == "disc":
            cur = get_disc_by_id(self.item["id"])
        else:
            cur = get_box_by_id(self.item["id"])
        new_name = self.name.value.strip() if self.allow_rename else (cur.get("name", "") if cur else "")
        new_desc = self.description.value.strip() if isinstance(self.description, toga.TextInput) else (cur.get("description", "") if cur else "")
        if self.comp_type == "disc":
            update_disc(self.item["id"], new_name, new_desc)
        else:
            update_box(self.item["id"], new_name, new_desc)

    def _apply(self, widget):
        qty = int(self.qty.value or 0)
        op = self.fixed_op or "set"
        try:
            self._save_meta()
            if self.comp_type == "disc":
                adjust_stock_disc(self.item["id"], qty, op)
            else:
                adjust_stock_box(self.item["id"], qty, op)
        except ValueError as e:
            self.error.text = str(e)
            return
        if self.on_save:
            self.on_save()
        self.close()


class WriteOffWindow(BaseWindow):
    """Списание по браку."""

    def __init__(self, comp_type, item, on_save=None, **kwargs):
        kwargs.setdefault("title", "Списание по браку")
        kwargs.setdefault("size", (420, 300))
        super().__init__(**kwargs)
        self.comp_type = comp_type
        self.item = item
        self.on_save = on_save
        self._build()

    def _build(self):
        box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        box.add(toga.Label(f"{self.item['name']}", style=Pack(margin=4, font_weight="bold", font_size=12)))
        box.add(toga.Label(f"Доступно: {self.item['quantity']}",
                           style=Pack(margin=4, color="#555555", font_size=12)))
        self.qty = toga.NumberInput(min=0, value=0, style=Pack(width=120, margin=4, font_size=12))
        self.reason = toga.TextInput(placeholder="Причина (брак)", style=Pack(flex=1, margin=4, font_size=12))
        self.error = toga.Label("", style=Pack(margin=4, color="#c0392b", font_size=12))

        box.add(_row(_label("Количество:"), self.qty))
        box.add(_row(_label("Причина:"), self.reason))
        box.add(self.error)
        box.add(_row(
            toga.Button("Отмена", on_press=lambda w: self.close(), style=Pack(flex=1, margin=4, font_size=12)),
            toga.Button("Списать", on_press=self._apply, style=Pack(flex=1, margin=4, font_size=12, background_color="#c0392b")),
        ))
        self.content = box

    def _apply(self, widget):
        qty = int(self.qty.value or 0)
        ok, msg = write_off_component(self.comp_type, self.item["id"], qty, self.reason.value.strip())
        if not ok:
            self.error.text = msg
            return
        if self.on_save:
            self.on_save()
        self.close()


class DispatchProductWindow(BaseWindow):
    """Списание одного комплекта с датой."""

    def __init__(self, product, on_save=None, main_window=None, **kwargs):
        kwargs.setdefault("title", "Списать ИК")
        kwargs.setdefault("size", (420, 300))
        super().__init__(**kwargs)
        self.product = product
        self.on_save = on_save
        self.main_window = main_window
        self._build()

    def _build(self):
        from datetime import date
        box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        box.add(toga.Label(f"{self.product['name']}", style=Pack(margin=4, font_weight="bold", font_size=12)))
        box.add(toga.Label(f"Доступно: {self.product.get('available', 0)}",
                            style=Pack(margin=4, color="#555555", font_size=12)))
        self.qty = toga.NumberInput(min=0, value=1, style=Pack(width=120, margin=4, font_size=12))
        self.date = toga.DateInput(value=date.today(), style=Pack(width=160, margin=4, font_size=12))
        self.error = toga.Label("", style=Pack(margin=4, color="#c0392b", font_size=12))

        box.add(_row(_label("Количество:"), self.qty))
        box.add(_row(_label("Дата:"), self.date))
        box.add(self.error)
        box.add(_row(
            toga.Button("Отмена", on_press=lambda w: self.close(), style=Pack(flex=1, margin=4, font_size=12)),
            toga.Button("Списать", on_press=self._apply, style=Pack(flex=1, margin=4, font_size=12, background_color="#c0392b")),
        ))
        self.content = box

    async def _apply(self, widget):
        qty = int(self.qty.value or 0)
        d = self.date.value
        dispatch_date = d.strftime("%Y-%m-%d") if d else None
        ok, msg = dispatch_product(self.product["id"], qty, dispatch_date)
        if not ok:
            self.error.text = msg
            return
        if self.main_window:
            await self.main_window.dialog(toga.InfoDialog("Успех", msg))
        if self.on_save:
            self.on_save()
        self.close()


class ProductComponentRow(toga.Box):
    """Одна строка компонента продукта."""

    def __init__(self, discs, boxes, comp=None):
        super().__init__(style=Pack(direction=ROW, margin=4))
        self.discs = discs
        self.boxes = boxes
        disc_names = ["—"] + [d["name"] for d in discs]
        box_names = ["—"] + [b["name"] for b in boxes]
        self.disc_spin = toga.Selection(items=disc_names, style=Pack(flex=2, margin=2, font_size=12))
        self.disc_qty = toga.NumberInput(min=0, value=0, style=Pack(width=70, margin=2, font_size=12))
        self.box_spin = toga.Selection(items=box_names, style=Pack(flex=2, margin=2, font_size=12))
        self.box_qty = toga.NumberInput(min=0, value=0, style=Pack(width=70, margin=2, font_size=12))
        self.add(toga.Label("Диск:", style=Pack(width=45, margin=2, font_size=12)))
        self.add(self.disc_spin)
        self.add(self.disc_qty)
        self.add(toga.Label("Коробка:", style=Pack(width=60, margin=2, font_size=12)))
        self.add(self.box_spin)
        self.add(self.box_qty)
        self.add(toga.Button("✕", on_press=lambda w: self._remove(),
                             style=Pack(width=45, margin=2, font_size=12, background_color="#c0392b")))
        if comp:
            self._fill(comp)

    def _fill(self, comp):
        if comp.get("disc_id"):
            d = get_disc_by_id(comp["disc_id"])
            if d:
                self.disc_spin.value = d["name"]
                self.disc_qty.value = comp.get("disc_quantity", 0)
        if comp.get("box_id"):
            b = get_box_by_id(comp["box_id"])
            if b:
                self.box_spin.value = b["name"]
                self.box_qty.value = comp.get("box_quantity", 0)

    def _remove(self):
        if self.parent:
            self.parent.remove(self)

    def collect(self):
        disc_name = self.disc_spin.value if self.disc_spin.value != "—" else None
        box_name = self.box_spin.value if self.box_spin.value != "—" else None
        dq = int(self.disc_qty.value or 0)
        bq = int(self.box_qty.value or 0)
        if not disc_name and not box_name:
            return None
        comp = {}
        if disc_name:
            d = next((x for x in self.discs if x["name"] == disc_name), None)
            if d:
                comp["disc_id"] = d["id"]
                comp["disc_quantity"] = dq
        if box_name:
            b = next((x for x in self.boxes if x["name"] == box_name), None)
            if b:
                comp["box_id"] = b["id"]
                comp["box_quantity"] = bq
        return comp


class AddEditProductWindow(BaseWindow):
    """Добавление/редактирование продукта с компонентами."""

    def __init__(self, product_id=None, on_save=None, **kwargs):
        kwargs.setdefault("title", "Добавить комплект" if product_id is None else "Редактировать комплект")
        kwargs.setdefault("size", (640, 620))
        super().__init__(**kwargs)
        self.product_id = product_id
        self.on_save = on_save
        self.discs = [{"id": d.doc_id, "name": d["name"]} for d in get_all_discs()]
        self.boxes = [{"id": b.doc_id, "name": b["name"]} for b in get_all_boxes()]
        self._build()

    def _build(self):
        root = toga.Box(style=Pack(direction=COLUMN, margin=10))
        self.name = toga.TextInput(placeholder="Название комплекта", style=Pack(flex=1, margin=4, font_size=12))
        self.code = toga.TextInput(placeholder="Код", style=Pack(width=140, margin=4, font_size=12))
        self.desc = toga.TextInput(placeholder="Описание", style=Pack(flex=1, margin=4, font_size=12))
        self.error = toga.Label("", style=Pack(margin=4, color="#c0392b", font_size=12))

        root.add(_row(_label("Название:"), self.name))
        root.add(_row(_label("Код:"), self.code))
        root.add(_row(_label("Описание:"), self.desc))
        root.add(toga.Label("Компоненты:", style=Pack(margin=4, font_weight="bold", font_size=12)))
        root.add(self.error)

        self.comp_box = toga.Box(style=Pack(direction=COLUMN, margin=4))
        sc = toga.ScrollContainer(vertical=True, horizontal=False, style=Pack(height=240, margin=4))
        sc.content = self.comp_box
        root.add(sc)

        root.add(toga.Button("+ Добавить компонент", on_press=lambda w: self._add_row(),
                             style=Pack(margin=6, font_size=12, background_color="#4472C4")))

        actions = toga.Box(style=Pack(direction=ROW, margin=6))
        actions.add(toga.Button("Отмена", on_press=lambda w: self.close(), style=Pack(flex=1, margin=4, font_size=12)))
        actions.add(toga.Button("Сохранить", on_press=self._save, style=Pack(flex=1, margin=4, font_size=12, background_color="#27ae60")))
        root.add(actions)

        self.content = root

        if self.product_id is not None:
            self._prefill()
        else:
            self._add_row()

    def _add_row(self, comp=None):
        self.comp_box.add(ProductComponentRow(self.discs, self.boxes, comp=comp))

    def _prefill(self):
        p = get_product_by_id(self.product_id)
        if not p:
            return
        self.name.value = p.get("name", "")
        self.code.value = p.get("code", "")
        self.desc.value = p.get("description", "")
        for comp in get_product_components(self.product_id):
            self._add_row(comp)

    def _save(self, widget):
        name = self.name.value.strip()
        if not name:
            self.error.text = "Введите название комплекта"
            return
        comps = []
        for row in list(self.comp_box.children):
            c = row.collect()
            if c:
                comps.append(c)
        try:
            if self.product_id is None:
                add_product_with_components(name, self.code.value.strip(),
                                            self.desc.value.strip(), comps)
            else:
                update_product_with_components(self.product_id, name,
                                               self.code.value.strip(),
                                               self.desc.value.strip(), comps)
        except Exception as e:
            self.error.text = str(e)
            return
        if self.on_save:
            self.on_save()
        self.close()
