from odoo.tests import tagged
from odoo.exceptions import UserError
from .common import TestCommon


@tagged('post_install', '-at_install')
class TestFreightUnlink(TestCommon):

    def setUp(self):
        super(TestFreightUnlink, self).setUp()

        self.env.company.prevent_unlink_sales_having_transport_related = True
        self.sale_order = self.sea_multiple_leg_route_sea_fcl_40ft
        self.sale_order._action_confirm()
        self.shipment = self.sale_order.shipment_id
        self.sale_order.state = 'draft'

    def test_unlink_with_shipment(self):
        """Test preventing unlink of sale order line with shipment"""
        self.shipment.freight_route_ids.unlink()

        with self.assertRaises(UserError):
            self.sale_order.order_line.unlink()

    def test_unlink_without_shipment_or_route(self):
        """Test unlink when no shipment or route exists"""
        self.shipment.unlink()  # route on sol is removed

        try:
            self.sale_order.order_line.unlink()
        except Exception as e:
            self.fail(f"Unexpected error when unlinking: {e}")
