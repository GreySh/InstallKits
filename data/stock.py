"""
Модуль для управления остатками.
"""

from .db import get_database, get_table
from tinydb import Query
from .operations import add_operation
from .products import get_product_by_id, get_product_components
from .discs import get_disc_by_id
from .boxes import get_box_by_id


def get_product_available_quantity(product_id):
    """Получить доступное количество комплектов по продукту."""
    components = get_product_components(product_id)
    if not components:
        return 0

    min_quantity = float('inf')
    for comp in components:
        disc_qty = float('inf')
        box_qty = float('inf')

        if comp.get('disc_id') and comp.get('disc_quantity', 0) > 0:
            disc_qty = get_stock_disc_quantity(comp['disc_id']) // comp['disc_quantity']
        if comp.get('box_id') and comp.get('box_quantity', 0) > 0:
            box_qty = get_stock_box_quantity(comp['box_id']) // comp['box_quantity']

        min_quantity = min(min_quantity, disc_qty, box_qty)

    return 0 if min_quantity == float('inf') else int(min_quantity)


def _build_dispatch_details(components, quantity):
    """Сформировать детали операции списания."""
    details = {
        'components': [],
        'kits_count': quantity,
    }

    for comp in components:
        disc_id = comp.get('disc_id')
        box_id = comp.get('box_id')
        disc_qty = comp.get('disc_quantity', 0)
        box_qty = comp.get('box_quantity', 0)

        if disc_id and disc_qty > 0:
            total_disc_needed = disc_qty * quantity
            disc = get_disc_by_id(disc_id)
            details['components'].append({
                'type': 'disc',
                'name': disc['name'] if disc else 'Неизвестно',
                'quantity_per_set': disc_qty,
                'total_quantity': total_disc_needed,
            })

        if box_id and box_qty > 0:
            total_box_needed = box_qty * quantity
            box = get_box_by_id(box_id)
            details['components'].append({
                'type': 'box',
                'name': box['name'] if box else 'Неизвестно',
                'quantity_per_set': box_qty,
                'total_quantity': total_box_needed,
            })

    return details


def _aggregate_component_needs(items):
    """Подсчитать суммарную потребность в компонентах для пакетного списания."""
    disc_needs = {}
    box_needs = {}

    for product_id, quantity in items:
        components = get_product_components(product_id)
        for comp in components:
            disc_id = comp.get('disc_id')
            box_id = comp.get('box_id')
            disc_qty = comp.get('disc_quantity', 0)
            box_qty = comp.get('box_quantity', 0)

            if disc_id and disc_qty > 0:
                disc_needs[disc_id] = disc_needs.get(disc_id, 0) + disc_qty * quantity
            if box_id and box_qty > 0:
                box_needs[box_id] = box_needs.get(box_id, 0) + box_qty * quantity

    return disc_needs, box_needs


def dispatch_product(product_id, quantity, dispatch_date=None):
    """
    Списать комплекты одного продукта.

    Returns:
        tuple: (success: bool, message: str)
    """
    if quantity <= 0:
        return False, 'Количество должно быть положительным числом'

    product = get_product_by_id(product_id)
    if not product:
        return False, 'Продукт не найден'

    components = get_product_components(product_id)
    if not components:
        return False, f'Продукт "{product["name"]}" не имеет компонентов'

    available = get_product_available_quantity(product_id)
    if quantity > available:
        return False, (
            f'Недостаточно комплектов "{product["name"]}". '
            f'Требуется {quantity}, доступно {available}'
        )

    for comp in components:
        disc_id = comp.get('disc_id')
        box_id = comp.get('box_id')
        disc_qty = comp.get('disc_quantity', 0)
        box_qty = comp.get('box_quantity', 0)

        if disc_id and disc_qty > 0:
            total_disc_needed = disc_qty * quantity
            current_disc_stock = get_stock_disc_quantity(disc_id)
            if current_disc_stock < total_disc_needed:
                disc = get_disc_by_id(disc_id)
                disc_name = disc['name'] if disc else 'Неизвестно'
                return False, (
                    f'Недостаточно носителей "{disc_name}". '
                    f'Требуется {total_disc_needed}, есть {current_disc_stock}'
                )

        if box_id and box_qty > 0:
            total_box_needed = box_qty * quantity
            current_box_stock = get_stock_box_quantity(box_id)
            if current_box_stock < total_box_needed:
                box = get_box_by_id(box_id)
                box_name = box['name'] if box else 'Неизвестно'
                return False, (
                    f'Недостаточно коробок "{box_name}". '
                    f'Требуется {total_box_needed}, есть {current_box_stock}'
                )

    for comp in components:
        disc_id = comp.get('disc_id')
        box_id = comp.get('box_id')
        disc_qty = comp.get('disc_quantity', 0)
        box_qty = comp.get('box_quantity', 0)

        if disc_id and disc_qty > 0:
            adjust_stock_disc(disc_id, disc_qty * quantity, 'subtract', log_operation=False)
        if box_id and box_qty > 0:
            adjust_stock_box(box_id, box_qty * quantity, 'subtract', log_operation=False)

    details = _build_dispatch_details(components, quantity)
    add_operation('dispatch', product_id, quantity, details, dispatch_date)

    component_details = '; '.join(
        f"{c['type'].upper()}: {c['name']} ({c['total_quantity']} шт.)"
        for c in details['components']
    )
    message = f'Комплект "{product["name"]}" списан успешно! {quantity} шт.'
    if component_details:
        message += f' [{component_details}]'
    return True, message


def dispatch_products_batch(items, dispatch_date=None):
    """
    Списать несколько продуктов за одну операцию.

    Args:
        items: список кортежей (product_id, quantity)
        dispatch_date: дата операции (опционально)

    Returns:
        tuple: (success: bool, messages: list[str])
    """
    dispatch_items = []
    for product_id, quantity in items:
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return False, ['Некорректное количество для списания']

        if quantity > 0:
            dispatch_items.append((product_id, quantity))

    if not dispatch_items:
        return False, ['Укажите количество для списания хотя бы по одному продукту']

    for product_id, quantity in dispatch_items:
        product = get_product_by_id(product_id)
        if not product:
            return False, ['Один из выбранных продуктов не найден']

        components = get_product_components(product_id)
        if not components:
            return False, [f'Продукт "{product["name"]}" не имеет компонентов']

        available = get_product_available_quantity(product_id)
        if quantity > available:
            return False, [
                f'Недостаточно комплектов "{product["name"]}". '
                f'Требуется {quantity}, доступно {available}'
            ]

    disc_needs, box_needs = _aggregate_component_needs(dispatch_items)

    for disc_id, needed in disc_needs.items():
        current = get_stock_disc_quantity(disc_id)
        if current < needed:
            disc = get_disc_by_id(disc_id)
            disc_name = disc['name'] if disc else 'Неизвестно'
            return False, [
                f'Недостаточно носителей "{disc_name}". '
                f'Требуется {needed}, есть {current}'
            ]

    for box_id, needed in box_needs.items():
        current = get_stock_box_quantity(box_id)
        if current < needed:
            box = get_box_by_id(box_id)
            box_name = box['name'] if box else 'Неизвестно'
            return False, [
                f'Недостаточно коробок "{box_name}". '
                f'Требуется {needed}, есть {current}'
            ]

    messages = []
    for product_id, quantity in dispatch_items:
        success, message = dispatch_product(product_id, quantity, dispatch_date)
        if not success:
            return False, [message]
        messages.append(message)

    return True, messages


def get_stock_disc_quantity(disc_id):
    """Получить количество дисков на остатке."""
    db = get_database()
    stock_table = get_table(db, 'stock_discs')
    record = stock_table.get(Query().disc_id == disc_id)
    return record['quantity'] if record else 0


def get_stock_box_quantity(box_id):
    """Получить количество коробок на остатке."""
    db = get_database()
    stock_table = get_table(db, 'stock_boxes')
    record = stock_table.get(Query().box_id == box_id)
    return record['quantity'] if record else 0


def adjust_stock_disc(disc_id, quantity, operation='set', log_operation=True):
    """
    Корректировка остатка дисков.
    
    Args:
        disc_id: ID диска
        quantity: Количество
        operation: Операция 'set' (установить), 'add' (прибавить), 'subtract' (вычесть)
        log_operation: Записать ли операцию в историю
    
    Returns:
        bool: True если успешно, False если диска нет
    """
    stock_table = get_table(get_database(), 'stock_discs')
    
    record = stock_table.get(Query().disc_id == disc_id)
    if not record:
        print(f"Warning:Disc with ID {disc_id} not found in stock")
        return False
    
    current_quantity = record['quantity']
    
    if operation == 'add':
        new_quantity = current_quantity + quantity
        change_desc = f'+{quantity}'
    elif operation == 'subtract':
        new_quantity = current_quantity - quantity
        change_desc = f'-{quantity}'
    else:  # 'set'
        new_quantity = quantity
        change_desc = f'{current_quantity} to {quantity}'
    
    if new_quantity < 0:
        print(f"Error:Quantity would be negative ({new_quantity})")
        raise ValueError("Количество не может быть отрицательным")
    
    stock_table.update({'quantity': new_quantity}, doc_ids=[record.doc_id])
    print(f"Updated disc {disc_id}: {current_quantity} -> {new_quantity} ({operation} {quantity})")
    
    # Записать операцию в историю только если явно требуется
    if log_operation:
        from .discs import get_disc_by_id
        disc = get_disc_by_id(disc_id)
        disc_name = disc['name'] if disc else 'Неизвестно'
        
        details = {
            'components': [{'type': 'disc', 'name': disc_name, 'quantity': new_quantity}],
            'total_quantity': new_quantity,
            'operation': operation,
            'change': change_desc
        }
        add_operation('adjust_stock', None, new_quantity, details)
    
    return True


def adjust_stock_box(box_id, quantity, operation='set', log_operation=True):
    """
    Корректировка остатка коробок.
    
    Args:
        box_id: ID коробки
        quantity: Количество
        operation: Операция 'set' (установить), 'add' (прибавить), 'subtract' (вычесть)
        log_operation: Записать ли операцию в историю
    
    Returns:
        bool: True если успешно, False если коробки нет
    """
    stock_table = get_table(get_database(), 'stock_boxes')
    
    record = stock_table.get(Query().box_id == box_id)
    if not record:
        print(f"Warning:Box with ID {box_id} not found in stock")
        return False
    
    current_quantity = record['quantity']
    
    if operation == 'add':
        new_quantity = current_quantity + quantity
        change_desc = f'+{quantity}'
    elif operation == 'subtract':
        new_quantity = current_quantity - quantity
        change_desc = f'-{quantity}'
    else:  # 'set'
        new_quantity = quantity
        change_desc = f'{current_quantity} to {quantity}'
    
    if new_quantity < 0:
        print(f"Error:Quantity would be negative ({new_quantity})")
        raise ValueError("Количество не может быть отрицательным")
    
    stock_table.update({'quantity': new_quantity}, doc_ids=[record.doc_id])
    print(f"Updated box {box_id}: {current_quantity} -> {new_quantity} ({operation} {quantity})")
    
    # Записать операцию в историю только если явно требуется
    if log_operation:
        from .boxes import get_box_by_id
        box = get_box_by_id(box_id)
        box_name = box['name'] if box else 'Неизвестно'
        
        details = {
            'components': [{'type': 'box', 'name': box_name, 'quantity': new_quantity}],
            'total_quantity': new_quantity,
            'operation': operation,
            'change': change_desc
        }
        add_operation('adjust_stock', None, new_quantity, details)
    
    return True


def add_stock_disc(disc_id, quantity):
    """Добавить диски на остаток."""
    if quantity <= 0:
        raise ValueError("Количество должно быть положительным")
    
    from .discs import get_disc_by_id
    disc = get_disc_by_id(disc_id)
    disc_name = disc['name'] if disc else 'Неизвестно'
    
    current = get_stock_disc_quantity(disc_id)
    result = adjust_stock_disc(disc_id, current + quantity, log_operation=False)
    
    # Записать операцию
    if result:
        details = {
            'components': [{'type': 'disc', 'name': disc_name, 'quantity': quantity}],
            'total_quantity': quantity
        }
        add_operation('add_disc', None, quantity, details)
    
    return result


def add_stock_box(box_id, quantity):
    """Добавить коробки на остаток."""
    if quantity <= 0:
        raise ValueError("Количество должно быть положительным")
    
    from .boxes import get_box_by_id
    box = get_box_by_id(box_id)
    box_name = box['name'] if box else 'Неизвестно'
    
    current = get_stock_box_quantity(box_id)
    result = adjust_stock_box(box_id, current + quantity, log_operation=False)
    
    # Записать операцию
    if result:
        details = {
            'components': [{'type': 'box', 'name': box_name, 'quantity': quantity}],
            'total_quantity': quantity
        }
        add_operation('add_box', None, quantity, details)
    
    return result


def write_off_component(component_type, component_id, quantity, reason=''):
    """
    Списать компонент по браку.

    Args:
        component_type: 'disc' или 'box'
        component_id: ID компонента
        quantity: количество к списанию (> 0)
        reason: причина списания (брак)

    Returns:
        tuple: (success: bool, message: str)
    """
    if quantity <= 0:
        return False, 'Количество должно быть положительным числом'

    if component_type == 'disc':
        current = get_stock_disc_quantity(component_id)
        if current < quantity:
            disc = get_disc_by_id(component_id)
            name = disc['name'] if disc else 'Неизвестно'
            return False, f'Недостаточно носителей "{name}". Есть {current}, нужно списать {quantity}'

        adjust_stock_disc(component_id, quantity, 'subtract', log_operation=False)
        disc = get_disc_by_id(component_id)
        name = disc['name'] if disc else 'Неизвестно'

        details = {
            'components': [{'type': 'disc', 'name': name, 'quantity': quantity}],
            'total_quantity': quantity,
            'reason': reason,
        }
        add_operation('write_off', None, quantity, details)
        return True, f'Списано по браку: {name} — {quantity} шт.'

    elif component_type == 'box':
        current = get_stock_box_quantity(component_id)
        if current < quantity:
            box = get_box_by_id(component_id)
            name = box['name'] if box else 'Неизвестно'
            return False, f'Недостаточно коробок "{name}". Есть {current}, нужно списать {quantity}'

        adjust_stock_box(component_id, quantity, 'subtract', log_operation=False)
        box = get_box_by_id(component_id)
        name = box['name'] if box else 'Неизвестно'

        details = {
            'components': [{'type': 'box', 'name': name, 'quantity': quantity}],
            'total_quantity': quantity,
            'reason': reason,
        }
        add_operation('write_off', None, quantity, details)
        return True, f'Списано по браку: {name} — {quantity} шт.'

    return False, 'Неверный тип компонента'


def get_all_stock_discs():
    """Получить все остатки дисков с информацией о дисках."""
    db = get_database()
    stock_table = get_table(db, 'stock_discs')
    discs_table = get_table(db, 'discs')
    
    result = []
    for record in stock_table.all():
        disc = discs_table.get(doc_id=record['disc_id'])
        if disc:
            result.append({
                'disc_id': record['disc_id'],
                'disc_name': disc['name'],
                'quantity': record['quantity']
            })
    return result


def get_all_stock_boxes():
    """Получить все остатки коробок с информацией о коробках."""
    db = get_database()
    stock_table = get_table(db, 'stock_boxes')
    boxes_table = get_table(db, 'boxes')
    
    result = []
    for record in stock_table.all():
        box = boxes_table.get(doc_id=record['box_id'])
        if box:
            result.append({
                'box_id': record['box_id'],
                'box_name': box['name'],
                'quantity': record['quantity']
            })
    return result
