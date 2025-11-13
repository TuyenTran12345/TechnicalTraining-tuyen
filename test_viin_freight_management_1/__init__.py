from . import models
from . import controllers
from . import reports
from . import wizards

from odoo.tools.sql import column_exists, create_column


def pre_init_hook(cr):
    """Pre-populate some computed fields so that we can control how they
    are computed in post_init_hook later
    """
    if not column_exists(cr, 'sale_order', 'shipment_id'):
        create_column(cr, 'sale_order', 'shipment_id', 'integer')
    if not column_exists(cr, 'sale_order_line', 'shipment_id'):
        create_column(cr, 'sale_order_line', 'shipment_id', 'integer')
    if not column_exists(cr, 'sale_order_line', 'freight_route_id'):
        create_column(cr, 'sale_order_line', 'freight_route_id', 'integer')
