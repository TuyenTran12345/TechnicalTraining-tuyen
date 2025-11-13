from odoo import fields
from odoo.tests import tagged

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestFreightRouteFeatures(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestFreightRouteFeatures, cls).setUpClass()

    def test_001_route_name_sequence(self):
        """Test Case: Test automatic sequence for route name

        Route name must be generated automatically from sequence with correct format.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        route = self.env['freight.route'].create({
            'shipment_id': shipment.id,
            'transport_mode': 'sea',
            'route_type': 'main_carriage',
        })

        self.assertNotEqual(route.name, 'New', "Name must be generated from sequence, not 'New'")
        self.assertIn(shipment.name, route.name, "Name must contain shipment reference")

    def test_002_name_get_method(self):
        """Test Case: Test name_get method

        Name_get must return correct format with route type.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        route = self.env['freight.route'].create({
            'shipment_id': shipment.id,
            'route_type': 'main_carriage',
            'name': 'TEST-ROUTE-001',
            'origin_id': self.dinhvu_port.id,
            'destination_id': self.la_port.id,
        })

        name_get_result = route.name_get()
        display_name = name_get_result[0][1]

        self.assertIn('MAIN', display_name, "Display name must contain uppercase route type")
        self.assertIn(route.origin_id.name, display_name, "Display name must contain origin name")
        self.assertIn(route.destination_id.name, display_name, "Display name must contain destination name")

    def test_003_compute_cargo_commodity_ids_from_packages(self):
        """Test Case: Test compute cargo_commodity_ids from packages

        Cargo_commodity_ids must be computed from packages when packages exist.
        """
        so = self.sea_multiple_leg_route_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        hn_hp_route = shipment.freight_route_ids.filtered(lambda r: r.route_id == self.route_hanoi_hai_phong)
        dv_la_route = shipment.freight_route_ids.filtered(lambda r: r.route_id == self.route_dinhvu_usa)

        shipment.write({
            'house_bill_number': "HBL-20250524-001-VN-DV",
            'direction': 'export',
        })

        self.env['cargo.template'].create({
            'name': 'Test Cargo Template',
            'shipment_id': shipment.id,
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'quantity': 2
        })
        shipment.generator_from_cargo_templates()

        # Create packages and cargo commodities
        package = shipment.package_ids[0]
        package2 = shipment.package_ids[1]

        cargo_commodity1 = package.cargo_commodity_ids[0]
        cargo_commodity2 = package2.cargo_commodity_ids[0]

        # Assign package to route
        hn_hp_route.package_ids = [(4, package.id)]
        dv_la_route.package_ids = [(4, package2.id)]

        # Cargo_commodity_ids must be computed from packages
        self.assertIn(cargo_commodity1, hn_hp_route.cargo_commodity_ids, "Cargo_commodity_ids must contain cargo_commodity1 from package")
        self.assertIn(cargo_commodity2, dv_la_route.cargo_commodity_ids, "Cargo_commodity_ids must contain cargo_commodity2 from package")

    def test_006_compute_third_party_ids_from_shipment(self):
        """Test Case: Test compute third_party_ids from shipment

        Third party ids must include all related parties from shipment.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        # Set information for shipment
        shipment.write({
            'shipper_id': self.shipper.id,
            'consignee_id': self.consignee.id,
        })

        route = self.env['freight.route'].create({
            'shipment_id': shipment.id,
            'agent_id': self.agent.id if hasattr(self, 'agent') and self.agent else False,
            'notify_party_id': self.notify_party.id,
            'route_type': 'main_carriage',
        })

        expected_parties = [self.consignee, self.notify_party, self.shipper]
        if hasattr(self, 'agent') and self.agent:
            expected_parties.append(self.agent)

        for party in expected_parties:
            self.assertIn(party, route.third_party_ids, f"Third parties must contain {party.name}")

    def test_007_compute_last_tracking_status_with_tracking(self):
        """Test Case: Test compute last_tracking_status with tracking

        Last tracking status must be taken from tracking record.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        route = self.env['freight.route'].create({
            'shipment_id': shipment.id,
            'route_type': 'main_carriage',
        })

        # Create tracking record
        tracking = self.env['freight.shipment.tracking'].create({
            'title_template_id': self.shipment_status_on_track.id,
            'shipment_id': shipment.id,
            'status': 'on_track',
            'event_time': fields.Datetime.now(),
        })

        route.last_tracking_id = tracking

        self.assertEqual(route.last_tracking_status, 'on_track', "Last tracking status must be taken from tracking")

    def test_008_compute_last_tracking_status_without_tracking(self):
        """Test Case: Test compute last_tracking_status without tracking

        Without tracking, last tracking status must be to_define.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        route = self.env['freight.route'].create({
            'shipment_id': shipment.id,
            'route_type': 'main_carriage',
        })

        # No tracking
        self.assertFalse(route.last_tracking_id, "No tracking yet")
        self.assertEqual(route.last_tracking_status, 'to_define', "Last tracking status must be to_define")

    def test_009_related_fields_from_shipment(self):
        """Test Case: Test related fields from shipment

        Shipper and consignee must be taken from shipment.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        # Set shipper and consignee for shipment
        shipment.write({
            'shipper_id': self.shipper.id,
            'consignee_id': self.consignee.id,
        })

        route = self.env['freight.route'].create({
            'shipment_id': shipment.id,
            'route_type': 'main_carriage',
        })

        self.assertEqual(route.shipper_id, self.shipper, "Shipper must be taken from shipment")
        self.assertEqual(route.consignee_id, self.consignee, "Consignee must be taken from shipment")

    def test_011_prepare_booking_vals_for_routes_single_carrier(self):
        """Test Case: Test _prepare_booking_vals_for_routes with single carrier

        Multiple routes with same carrier must create 1 multi-leg booking.
        """
        so = self.sea_multiple_leg_route_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]
        self.env['cargo.template'].create({
            'name': 'Test Cargo Template',
            'shipment_id': shipment.id,
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'quantity': 1
        })
        shipment.generator_from_cargo_templates()
        shipment.package_ids.write({
            'seal_number': '1234567890',
            'container_number': 'TEAU1234567',
        })

        # Set same carrier for all routes
        shipment.freight_route_ids.write({
            'carrier_id': self.maersk_carrier.id,
            'package_ids': [(6, 0, shipment.package_ids.ids)],
        })

        shipment.action_generate_bookings()

        self.assertEqual(len(shipment.booking_ids), 1, "Same carrier must create 1 booking")
        self.assertTrue(shipment.booking_ids[0].multiple_leg_route, "Must be multi-leg booking")
        self.assertEqual(shipment.booking_ids[0].carrier_id, self.maersk_carrier, "Carrier must be correct")

    def test_012_prepare_booking_vals_for_routes_multiple_carriers(self):
        """Test Case: Test _prepare_booking_vals_for_routes with multiple carriers

        Multiple routes with different carriers must create multiple bookings.
        """
        so = self.sea_multiple_leg_route_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        self.env['cargo.template'].create({
            'name': 'Test Cargo Template',
            'shipment_id': shipment.id,
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'quantity': 1
        })
        shipment.generator_from_cargo_templates()
        shipment.package_ids.write({
            'seal_number': '1234567890',
            'container_number': 'TEAU1234567',
        })

        route_hn_hp = shipment.freight_route_ids.filtered(lambda route: route.route_id == self.route_hanoi_hai_phong)
        route_dv_usa = shipment.freight_route_ids.filtered(lambda route: route.route_id == self.route_dinhvu_usa)

        route_hn_hp.write({
            'carrier_id': self.maersk_carrier.id,
            'package_ids': [(6, 0, shipment.package_ids.ids)],
        })
        route_dv_usa.write({
            'carrier_id': self.one_line_carrier.id,
            'package_ids': [(6, 0, shipment.package_ids.ids)],
        })

        shipment.action_generate_bookings()

        self.assertEqual(len(shipment.booking_ids), 2, "Different carriers must create multiple bookings")
        self.assertEqual(shipment.booking_ids[0].carrier_id, self.maersk_carrier, "Carrier must be correct")
        self.assertEqual(shipment.booking_ids[1].carrier_id, self.one_line_carrier, "Carrier must be correct")

    def test_013_prepare_booking_vals_single_route(self):
        """Test Case: Test _prepare_booking_vals for single route

        Single route must create single-leg booking with complete information.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]
        shipment.write({
            'carrier_id': self.maersk_carrier.id,
            'service_type': 'port_to_port',
        })
        self.env['cargo.template'].create({
            'name': 'Test Cargo Template',
            'shipment_id': shipment.id,
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'quantity': 1
        })
        shipment.generator_from_cargo_templates()
        shipment.package_ids.write({
            'seal_number': '1234567890',
            'container_number': 'TEAU1234567',
        })
        shipment.action_generate_bookings()
        self.assertEqual(len(shipment.booking_ids), 1, "Single route must create 1 booking")
        self.assertFalse(shipment.booking_ids[0].multiple_leg_route, "Must be single-leg booking")
        self.assertEqual(shipment.booking_ids[0].carrier_id, shipment.carrier_id, "Carrier must be correct")
        self.assertEqual(shipment.booking_ids[0].service_type, shipment.service_type, "Service type must be correct")
        self.assertEqual(shipment.booking_ids[0].transport_mode, shipment.transport_mode, "Transport mode must be correct")

    def test_014_action_set_status(self):
        """Test Case: Test action_set_transit_status

        Action must set freight_status and atd.
        """
        so = self.sea_multiple_leg_route_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        self.env['cargo.template'].create({
            'name': 'Test Cargo Template',
            'shipment_id': shipment.id,
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'quantity': 1
        })
        shipment.generator_from_cargo_templates()
        shipment.package_ids.write({
            'seal_number': '1234567890',
            'container_number': 'TEAU1234567',
        })

        route_hn_hp = shipment.freight_route_ids.filtered(lambda route: route.route_id == self.route_hanoi_hai_phong)
        route_dv_usa = shipment.freight_route_ids.filtered(lambda route: route.route_id == self.route_dinhvu_usa)
        route_hn_hp.write({
            'carrier_id': self.maersk_carrier.id,
            'package_ids': [(6, 0, shipment.package_ids.ids)],
        })
        route_dv_usa.write({
            'carrier_id': self.one_line_carrier.id,
            'package_ids': [(6, 0, shipment.package_ids.ids)],
        })

        route_hn_hp.action_set_in_transit()
        self.assertEqual(shipment.atd, route_hn_hp.atd, "Shipment ATD must be set")

        route_hn_hp.action_set_done()
        route_dv_usa.action_set_done()

        self.assertEqual(shipment.ata, route_dv_usa.ata, "Shipment ATA must be set")

        shipment.freight_route_ids.action_set_cancelled()
        self.assertFalse(route_hn_hp.atd, "ATD must be cleared")
        self.assertFalse(route_hn_hp.ata, "ATA must be cleared")
        self.assertFalse(route_dv_usa.atd, "ATD must be cleared")
        self.assertFalse(route_dv_usa.ata, "ATA must be cleared")

    def test_015_action_set_planned(self):
        """Test Case: Test action_set_planned

        Action must set freight_status and clear atd, ata.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        route = self.env['freight.route'].create({
            'shipment_id': shipment.id,
            'route_type': 'main_carriage',
            'freight_status': 'in_transit',
            'atd': fields.Datetime.now(),
            'ata': fields.Datetime.now(),
        })

        # Set planned
        route.action_set_planned()

        self.assertEqual(route.freight_status, 'planned', "Freight status must be planned")
        self.assertFalse(route.atd, "ATD must be cleared")
        self.assertFalse(route.ata, "ATA must be cleared")

    def test_019_route_freight_status_workflow(self):
        """Test Case: Test freight status workflow

        Route must be able to transition freight status according to correct workflow.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        route = self.env['freight.route'].create({
            'shipment_id': shipment.id,
            'route_type': 'main_carriage',
        })

        # Initially planned
        self.assertEqual(route.freight_status, 'planned', "Initial freight status must be planned")

        # Planned -> In Transit
        route.action_set_in_transit()
        self.assertEqual(route.freight_status, 'in_transit', "Freight status must change to in_transit")

        # In Transit -> Done
        route.action_set_done()
        self.assertEqual(route.freight_status, 'done', "Freight status must change to done")

        # Done -> Planned (can go back)
        route.action_set_planned()
        self.assertEqual(route.freight_status, 'planned', "Freight status must change back to planned")

        # Planned -> Cancelled
        route.action_set_cancelled()
        self.assertEqual(route.freight_status, 'cancelled', "Freight status must change to cancelled")

    def test_020_route_tracking_fields(self):
        """Test Case: Test tracking fields of route

        Freight_status field must have tracking=True.
        """
        route_fields = self.env['freight.route']._fields

        freight_status_field = route_fields.get('freight_status')
        self.assertTrue(getattr(freight_status_field, 'tracking', False), "Field freight_status must have tracking=True")
