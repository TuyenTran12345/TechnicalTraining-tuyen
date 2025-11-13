from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.exceptions import UserError

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestBookingFeatures(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestBookingFeatures, cls).setUpClass()

    def test_001_booking_name_sequence(self):
        """Test Case: Test automatic sequence for booking name

        Booking name must be generated automatically from sequence.
        """
        booking = self.env['freight.booking'].create({
            'booking_date': fields.Date.today(),
        })

        self.assertNotEqual(booking.name, 'New', "Name must be generated from sequence, not 'New'")
        self.assertTrue(booking.name.startswith('BK-'), "Name must start with prefix BK-")

    def test_002_compute_cargo_totals_from_packages(self):
        """Test Case: Test compute cargo totals from packages

        Booking must automatically calculate totals from packages (priority over cargo commodities).
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]
        shipment.write({
            'cargo_mode': 'structured_entry',
        })

        # Create packages with weight and volume
        package1 = self.env['freight.package'].create({
            'name': 'Container 40ft',
            'package_type_id': self.container_40gp.id,
            'shipment_id': shipment.id,
            'volume': 67.5,
        })

        package2 = self.env['freight.package'].create({
            'name': 'Pallet',
            'package_type_id': self.pallet_euro.id,
            'shipment_id': shipment.id,
            'volume': 2.0,
        })

        # Create cargo commodities and assign to packages
        self.env['cargo.commodity'].create([{
            'name': 'T-shirts',
            'shipment_id': shipment.id,
            'quantity': 100,
            'weight': 50.0,
            'volume': 2.5,
            'package_ids': [(4, package1.id)],
        }, {
            'name': 'Jeans',
            'shipment_id': shipment.id,
            'quantity': 50,
            'weight': 75.0,
            'volume': 3.0,
            'package_ids': [(4, package2.id)],
        }
        ])

        shipment.action_generate_bookings()
        booking = shipment.booking_id

        # Check totals calculated from packages (priority over cargo commodities)
        self.assertEqual(booking.total_packages, 2, "Total packages must equal 2")
        self.assertEqual(booking.total_cargo_commodities, 150, "Total cargo commodities must equal 100 + 50 = 150")
        self.assertEqual(booking.total_weight, package1.weight + package2.weight, "Total weight must equal sum of package weights")
        self.assertEqual(booking.total_volume, 69.5, "Total volume must equal 67.5 + 2.0 = 69.5")

    def test_003_compute_cargo_totals_from_cargo_commodities_only(self):
        """Test Case: Test compute cargo totals from cargo commodities when no packages

        When no packages exist, booking must calculate totals from cargo commodities.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]
        shipment.write({
            'cargo_commodity_ids': [(0, 0, {
                'name': 'T-shirts',
                'shipment_id': shipment.id,
                'quantity': 100,
                'weight': 50.0,
                'volume': 2.5,
            }), (0, 0, {
                'name': 'Jeans',
                'shipment_id': shipment.id,
                'quantity': 50,
                'weight': 75.0,
                'volume': 3.0,
            })],
            'cargo_mode': 'structured_entry',
        })
        shipment.action_generate_bookings()
        booking = shipment.booking_id

        # Check totals calculated from cargo commodities
        self.assertEqual(booking.total_packages, 0, "Total packages must equal 0")
        self.assertEqual(booking.total_cargo_commodities, 150, "Total cargo commodities must equal 100 + 50 = 150")
        self.assertEqual(booking.total_weight, 125.0, "Total weight must equal 50 + 75 = 125")
        self.assertEqual(booking.total_volume, 5.5, "Total volume must equal 2.5 + 3.0 = 5.5")

    def test_004_compute_schedule_multiple_leg_booking(self):
        """Test Case: Test compute schedule for multiple leg booking

        With multiple legs, schedule must be calculated from freight routes.
        """
        so = self.sea_multiple_leg_route_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        self.env['cargo.template'].create({
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'name': 'Test Cargo Template',
            'shipment_id': shipment.id,
            'quantity': 1,
        })
        shipment.generator_from_cargo_templates()
        package = shipment.package_ids[0]
        package.write({
            'seal_number': '1234567890',
            'container_number': 'TEAU1234567',
        })

        # Create freight routes for booking
        route_hn_hp = shipment.freight_route_ids.filtered(lambda r: r.route_id == self.route_hanoi_hai_phong)
        route_dv_us = shipment.freight_route_ids.filtered(lambda r: r.route_id == self.route_dinhvu_usa)
        route_hn_hp.write({
            'etd': fields.Datetime.now() + timedelta(days=4),
            'eta': fields.Datetime.now() + timedelta(days=25),
            'cutoff': fields.Datetime.now() + timedelta(days=2),
            'carrier_id': self.maersk_carrier.id,
            'package_ids': [(4, package.id)],
        })
        route_dv_us.write({
            'etd': fields.Datetime.now() + timedelta(days=4),
            'eta': fields.Datetime.now() + timedelta(days=25),
            'cutoff': fields.Datetime.now() + timedelta(days=2),
            'carrier_id': self.maersk_carrier.id,
            'package_ids': [(4, package.id)],
        })
        shipment.action_generate_bookings()
        booking = shipment.booking_id

        # Booking schedule must be calculated from routes
        self.assertEqual(booking.etd, route_hn_hp.etd, "Booking ETD must equal earliest ETD of routes")
        self.assertEqual(booking.eta, route_dv_us.eta, "Booking ETA must equal latest ETA of routes")
        self.assertEqual(booking.cutoff, route_hn_hp.cutoff, "Booking cutoff must equal earliest cutoff of routes")

    def test_005_check_booking_validity_multiple_leg_no_routes(self):
        """Test Case: Test validation for multiple leg booking without routes

        Multiple leg booking must have routes before confirmation.
        """
        so = self.sea_multiple_leg_route_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        self.env['cargo.template'].create({
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'name': 'Test Cargo Template',
            'shipment_id': shipment.id,
            'quantity': 1,
        })
        shipment.generator_from_cargo_templates()
        shipment.freight_route_ids.write({
            'carrier_id': self.maersk_carrier.id,
            'package_ids': [(6, 0, shipment.package_ids.ids)],
        })
        shipment.action_generate_bookings()
        booking = shipment.booking_id

        shipment.freight_route_ids.write({'booking_ids': [(5, 0, 0)]})

        # Try to confirm booking without routes - must raise UserError
        with self.assertRaises(UserError) as context:
            booking.action_confirm()

        self.assertIn('Please set a Route for the Booking', str(context.exception))

    def test_006_check_booking_validity_no_carrier(self):
        """Test Case: Test validation for multiple leg booking without carrier

        Multiple leg booking must have carrier before confirmation.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]
        shipment.write({
            'carrier_id': self.maersk_carrier.id,
        })

        self.env['cargo.template'].create({
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'name': 'Test Cargo Template',
            'shipment_id': shipment.id,
            'quantity': 1,
        })
        shipment.generator_from_cargo_templates()
        shipment.action_generate_bookings()
        booking = shipment.booking_id
        booking.write({
            'carrier_id': False,
        })
        # Try to confirm booking without routes - must raise UserError
        with self.assertRaises(UserError) as context:
            booking.action_confirm()

        self.assertIn('Please set a Carrier for the Booking', str(context.exception))

    def test_007_sync_info_single_leg_shipment(self):
        """Test Case: Test sync info for single leg shipment

        Confirmed booking must sync info directly to shipment.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]
        self.env['cargo.template'].create({
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'shipment_id': shipment.id,
            'name': 'Test Cargo Template',
            'quantity': 1,
        })
        shipment.generator_from_cargo_templates()
        shipment.package_ids.write({
            'seal_number': '1234567890',
            'container_number': 'TEAU1234567',
        })

        shipment.action_generate_bookings()
        booking = shipment.booking_id

        booking.write({
            'carrier_id': self.maersk_carrier.id,
            'vessel_name': 'MSC OSCAR',
            'vessel_voyage_number': 'V001',
        })
        booking.with_context(bypass_resolution_check=True).action_confirm()

        # Check info has been synced to shipment
        self.assertEqual(shipment.carrier_id, self.maersk_carrier, "Carrier must be synced to shipment")
        self.assertEqual(shipment.vessel_name, 'MSC OSCAR', "Vessel name must be synced")
        self.assertEqual(shipment.vessel_voyage_number, 'V001', "Vessel voyage must be synced")

    def test_008_sync_info_multiple_leg_shipment(self):
        """Test Case: Test sync info for multiple leg shipment

        Confirmed booking must sync info to routes instead of shipment.
        """
        so = self.sea_multiple_leg_route_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        self.env['cargo.template'].create({
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'shipment_id': shipment.id,
            'name': 'Test Cargo Template',
            'quantity': 1,
        })
        shipment.generator_from_cargo_templates()
        shipment.package_ids.write({
            'seal_number': '1234567890',
            'container_number': 'TEAU1234567',
        })
        route_hn_hp = shipment.freight_route_ids.filtered(lambda r: r.route_id == self.route_hanoi_hai_phong)
        route_dv_us = shipment.freight_route_ids.filtered(lambda r: r.route_id == self.route_dinhvu_usa)
        route_hn_hp.write({
            'etd': fields.Datetime.now() + timedelta(days=4),
            'eta': fields.Datetime.now() + timedelta(days=25),
            'cutoff': fields.Datetime.now() + timedelta(days=2),
            'carrier_id': self.maersk_carrier.id,
            'package_ids': [(6, 0, shipment.package_ids.ids)],
        })
        route_dv_us.write({
            'etd': fields.Datetime.now() + timedelta(days=4),
            'eta': fields.Datetime.now() + timedelta(days=25),
            'cutoff': fields.Datetime.now() + timedelta(days=2),
            'carrier_id': self.maersk_carrier.id,
            'package_ids': [(6, 0, shipment.package_ids.ids)],
        })
        shipment.action_generate_bookings()
        booking = shipment.booking_id
        booking.write({
            'carrier_id': self.agent.id,
        })
        booking.with_context(bypass_resolution_check=True).action_confirm()
        self.assertEqual(route_hn_hp.carrier_id, self.agent, "Carrier must be synced to route")
        self.assertEqual(route_dv_us.carrier_id, self.agent, "Carrier must be synced to route")

    def test_009_write_method_no_sync_for_non_sync_fields(self):
        """Test Case: Test write method does not sync when updating non-sync fields

        When updating non-sync fields, should not trigger sync info.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]
        self.env['cargo.template'].create({
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'shipment_id': shipment.id,
            'name': 'Test Cargo Template',
            'quantity': 1,
        })
        shipment.generator_from_cargo_templates()
        shipment.package_ids.write({
            'seal_number': '1234567890',
            'container_number': 'TEAU1234567',
        })

        shipment.action_generate_bookings()
        booking = shipment.booking_id

        booking.write({
            'vessel_name': 'MSC OSCAR',
            'vessel_voyage_number': 'V001',
        })

        # Check info has not been synced to shipment (booking not confirmed yet)
        self.assertEqual(shipment.vessel_name, False, "Unconfirmed booking should not sync info to Shipment")
        self.assertEqual(shipment.vessel_voyage_number, False, "Unconfirmed booking should not sync info to Shipment")
