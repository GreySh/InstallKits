"""
Пакет для работы с данными.
"""

from .db import get_database, get_table, clear_database
from .products import add_product, get_all_products, get_product_by_id, get_product_components, update_product, delete_product, add_product_with_components, update_product_with_components
from .discs import add_disc, get_all_discs, get_disc_by_id, get_disc_by_name, update_disc, delete_disc
from .boxes import add_box, get_all_boxes, get_box_by_id, get_box_by_name, update_box, delete_box
from .kits import add_kit_component, update_kit_component, delete_kit_component, get_kit_components, get_kit_component
from .stock import (
    get_stock_disc_quantity, get_stock_box_quantity,
    adjust_stock_disc, adjust_stock_box,
    add_stock_disc, add_stock_box,
    get_all_stock_discs, get_all_stock_boxes,
    get_product_available_quantity, dispatch_product, dispatch_products_batch
)
from .operations import add_operation, get_operations, get_operations_by_type, delete_operation

__all__ = [
    'get_database',
    'get_table',
    'clear_database',
    'add_product',
    'get_all_products',
    'get_product_by_id',
    'get_product_components',
    'update_product',
    'add_disc',
    'get_all_discs',
    'get_disc_by_id',
    'get_disc_by_name',
    'update_disc',
    'delete_disc',
    'add_box',
    'get_all_boxes',
    'get_box_by_id',
    'get_box_by_name',
    'update_box',
    'delete_box',
    'add_kit_component',
    'update_kit_component',
    'delete_kit_component',
    'get_kit_components',
    'get_kit_component',
    'get_stock_disc_quantity',
    'get_stock_box_quantity',
    'adjust_stock_disc',
    'adjust_stock_box',
    'add_stock_disc',
    'add_stock_box',
    'get_all_stock_discs',
    'get_all_stock_boxes',
    'get_product_available_quantity',
    'dispatch_product',
    'dispatch_products_batch',
    'add_operation',
    'get_operations',
    'get_operations_by_type',
    'delete_operation',
    'add_product_with_components',
    'update_product_with_components'
]
