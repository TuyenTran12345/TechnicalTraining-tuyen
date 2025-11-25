from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestDataIntegrity(TestCommon):
    """Test cases for data integrity in freight operations"""

    @classmethod
    def setUpClass(cls):
        super(TestDataIntegrity, cls).setUpClass()

    def test_01_cargo_commodity_data_integrity(self):
        """Test data integrity constraints for cargo commodities

        This test ensures that:
        1. Cargo commodities with booking status 'booked' cannot be modified
        2. Cargo commodities with booking status 'booked' cannot be deleted
        3. Booking status is correctly computed based on bookings
        """
        shipment = self.fcl_shipment_fcl_single_route

        cargo = self.env['cargo.commodity'].create({
            'name': 'Test Cargo Commodity',
            'shipment_id': shipment.id,
            'is_individual_package': True,
            'quantity': 30,
            'package_type_id': self.fiberboard_box.id,
            'weight': 22000,
            'volume': 33.2,
            'cargo_type_id': self.cargo_type_general.id,
            'hs_code_id': self.hs_code_6201.id,
            'country_of_origin_id': self.env.ref('base.vn').id,
            'handling_instructions': "Test handling instructions",
        })

        self.assertEqual(cargo.booking_status, 'need_booking', "Initial booking status should be 'need_booking'")

        shipment.action_generate_bookings()
        booking = shipment.booking_id
        self.assertTrue(booking, "Booking should be created")

        self.assertEqual(cargo.booking_status, 'booking_in_progress',
            "Booking status should be 'booking_in_progress' after booking creation")

        booking.action_confirm()

        self.assertEqual(cargo.booking_status, 'booked',
            "Booking status should be 'booked' after booking confirmation")

        with self.assertRaises(ValidationError, msg="Should not be able to modify booked cargo"):
            cargo.write({'name': 'Modified Name'})

        with self.assertRaises(ValidationError, msg="Should not be able to delete booked cargo"):
            cargo.unlink()

        booking.action_draft()

        cargo.write({'name': 'Modified Name'})
        self.assertEqual(cargo.name, 'Modified Name', "Cargo should be modifiable when booking is in draft state")

    def test_02_package_data_integrity(self):
        """Test data integrity constraints for packages

        This test ensures that:
        1. Packages with booking status 'booked' cannot be modified
        2. Packages with booking status 'booked' cannot be deleted
        3. Booking status is correctly computed based on bookings
        """
        shipment = self.fcl_shipment_fcl_single_route

        package = self.env['freight.package'].create({
            'name': 'Test Package',
            'shipment_id': shipment.id,
            'package_type_id': self.container_40gp.id,
            'weight': 22000,
            'volume': 33.2,
            'seal_number': "TEST001",
            'container_number': "TEST123456"
        })

        self.env['cargo.commodity'].create({
            'name': 'Test Cargo in Package',
            'shipment_id': shipment.id,
            'package_ids': [(6, 0, [package.id])],
            'is_individual_package': True,
            'quantity': 30,
            'package_type_id': self.fiberboard_box.id,
            'weight': 22000,
            'volume': 33.2,
            'cargo_type_id': self.cargo_type_general.id,
            'hs_code_id': self.hs_code_6201.id,
            'country_of_origin_id': self.env.ref('base.vn').id,
        })

        self.assertEqual(package.booking_status, 'need_booking', "Initial booking status should be 'need_booking'")

        shipment.action_generate_bookings()
        booking = shipment.booking_id
        self.assertTrue(booking, "Booking should be created")

        self.assertEqual(package.booking_status, 'booking_in_progress',
            "Booking status should be 'booking_in_progress' after booking creation")

        booking.action_confirm()

        self.assertEqual(package.booking_status, 'booked',
            "Booking status should be 'booked' after booking confirmation")

        with self.assertRaises(ValidationError, msg="Should not be able to modify booked package"):
            package.write({'name': 'Modified Package'})

        with self.assertRaises(ValidationError, msg="Should not be able to delete booked package"):
            package.unlink()

        booking.action_draft()

        package.write({'name': 'Modified Package'})
        self.assertEqual(package.name, 'Modified Package',
            "Package should be modifiable when booking is in draft state")

    def test_03_route_data_integrity(self):
        """Test data integrity constraints for routes

        This test ensures that:
        1. Routes with confirmed bookings cannot be deleted
        """
        shipment = self.fcl_shipment_fcl_single_route

        route1 = self.env['freight.route'].create({
            'name': 'Test Route 1',
            'shipment_id': shipment.id,
            'route_id': self.route_hanoi_hai_phong.id,
            'origin_id': self.hanoi_air_port.id,
            'destination_id': self.hai_phong_port.id,
            'transport_mode': 'land',
            'service_type': 'port_to_port',
            'land_shipping_method_id': self.shipping_method_fcl.id,
            'carrier_id': self.agent.id,
            'route_type': 'pickup',
            'etd': fields.Datetime.now(),
            'eta': fields.Datetime.now() + timedelta(days=1),
            'cutoff': fields.Datetime.now() - timedelta(days=1),
        })

        package = self.env['freight.package'].create({
            'name': 'Test Package for Route',
            'shipment_id': shipment.id,
            'package_type_id': self.container_40gp.id,
            'weight': 22000,
            'volume': 33.2,
            'seal_number': "TEST002",
            'container_number': "TEST654321"
        })

        route1.write({'package_ids': [(4, package.id)]})

        shipment.action_generate_bookings()
        booking = shipment.booking_ids.filtered(
            lambda b: b.carrier_id == self.agent)
        self.assertTrue(booking, "Booking should be created")

        booking.action_confirm()

        with self.assertRaises(ValidationError, msg="Should not be able to delete route with confirmed booking"):
            route1.unlink()

        booking.action_draft()

        route1.unlink()
        self.assertFalse(self.env['freight.route'].search([('id', '=', route1.id)]),
            "Route should be deleted when booking is in draft state")

    def test_04_booking_generation_from_cargo(self):
        """Test booking generation from cargo commodities

        This test ensures that:
        1. Bookings are correctly generated from cargo commodities
        2. Bookings are grouped by carrier to avoid duplicate bookings
        """
        shipment = self.fcl_shipment_fcl_single_route

        route1 = self.env['freight.route'].create({
            'name': 'Test Route 1',
            'shipment_id': shipment.id,
            'route_id': self.route_hanoi_hai_phong.id,
            'origin_id': self.hanoi_air_port.id,
            'destination_id': self.hai_phong_port.id,
            'transport_mode': 'land',
            'service_type': 'port_to_port',
            'land_shipping_method_id': self.shipping_method_fcl.id,
            'carrier_id': self.maersk_carrier.id,
            'route_type': 'pickup',
            'etd': fields.Datetime.now(),
            'eta': fields.Datetime.now() + timedelta(days=1),
            'cutoff': fields.Datetime.now() - timedelta(days=1),
        })

        route2 = self.env['freight.route'].create({
            'name': 'Test Route 2',
            'shipment_id': shipment.id,
            'route_id': self.route_dinhvu_usa.id,
            'origin_id': self.dinhvu_port.id,
            'destination_id': self.la_port.id,
            'transport_mode': 'sea',
            'service_type': 'port_to_port',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'carrier_id': self.maersk_carrier.id,
            'route_type': 'main_carriage',
            'etd': fields.Datetime.now() + timedelta(days=2),
            'eta': fields.Datetime.now() + timedelta(days=30),
            'cutoff': fields.Datetime.now() + timedelta(days=1),
        })

        cargo1 = self.env['cargo.commodity'].create({
            'name': 'Test Cargo 1',
            'shipment_id': shipment.id,
            'is_individual_package': True,
            'quantity': 30,
            'package_type_id': self.fiberboard_box.id,
            'weight': 10000,
            'volume': 15.0,
            'cargo_type_id': self.cargo_type_general.id,
            'hs_code_id': self.hs_code_6201.id,
            'country_of_origin_id': self.env.ref('base.vn').id,
        })
        cargo1.write({
            'weight': 10000,
            'volume': 15.0,
            'route_ids': [(6, 0, [route1.id, route2.id])],
        })

        cargo2 = self.env['cargo.commodity'].create({
            'name': 'Test Cargo 2',
            'shipment_id': shipment.id,
            'is_individual_package': True,
            'quantity': 20,
            'package_type_id': self.fiberboard_box.id,
            'weight': 12000,
            'volume': 18.2,
            'cargo_type_id': self.cargo_type_general.id,
            'hs_code_id': self.hs_code_6201.id,
            'country_of_origin_id': self.env.ref('base.vn').id,
        })
        cargo2.write({
            'quantity': 20,
            'weight': 12000,
            'volume': 18.2,
            'route_ids': [(6, 0, [route1.id, route2.id])],
        })

        shipment.action_generate_bookings()

        self.assertEqual(
            len(shipment.booking_ids), 1,
            "Only one booking should be created for routes with the same carrier")

        booking = shipment.booking_ids[0]

        self.assertEqual(
            len(booking.cargo_commodity_ids), 2,
            "Booking should contain both cargo commodities")
        self.assertIn(
            cargo1.id, booking.cargo_commodity_ids.ids,
            "Booking should contain cargo1")
        self.assertIn(
            cargo2.id, booking.cargo_commodity_ids.ids,
            "Booking should contain cargo2")

        self.assertEqual(
            len(booking.freight_route_ids), 2,
            "Booking should be linked to both routes")
        self.assertIn(
            route1.id, booking.freight_route_ids.ids,
            "Booking should be linked to route1")
        self.assertIn(
            route2.id, booking.freight_route_ids.ids,
            "Booking should be linked to route2")

        self.assertTrue(
            booking.multiple_leg_route,
            "Booking should have multiple_leg_route flag set to True")

    def test_05_booking_generation_from_package(self):
        """Test booking generation from packages

        This test ensures that:
        1. Bookings are correctly generated from packages
        2. Bookings are grouped by carrier to avoid duplicate bookings
        """
        shipment = self.fcl_shipment_fcl_single_route

        route1 = self.env['freight.route'].create({
            'name': 'Test Route 1',
            'shipment_id': shipment.id,
            'route_id': self.route_hanoi_hai_phong.id,
            'origin_id': self.hanoi_air_port.id,
            'destination_id': self.hai_phong_port.id,
            'transport_mode': 'land',
            'service_type': 'port_to_port',
            'land_shipping_method_id': self.shipping_method_fcl.id,
            'carrier_id': self.agent.id,
            'route_type': 'pickup',
            'etd': fields.Datetime.now(),
            'eta': fields.Datetime.now() + timedelta(days=1),
            'cutoff': fields.Datetime.now() - timedelta(days=1),
        })

        route2 = self.env['freight.route'].create({
            'name': 'Test Route 2',
            'shipment_id': shipment.id,
            'route_id': self.route_dinhvu_usa.id,
            'origin_id': self.dinhvu_port.id,
            'destination_id': self.la_port.id,
            'transport_mode': 'sea',
            'service_type': 'port_to_port',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'carrier_id': self.maersk_carrier.id,
            'route_type': 'main_carriage',
            'etd': fields.Datetime.now() + timedelta(days=2),
            'eta': fields.Datetime.now() + timedelta(days=30),
            'cutoff': fields.Datetime.now() + timedelta(days=1),
        })

        package1 = self.env['freight.package'].create({
            'name': 'Test Package 1',
            'shipment_id': shipment.id,
            'package_type_id': self.container_40gp.id,
            'weight': 22000,
            'volume': 33.2,
            'seal_number': "TEST003",
            'container_number': "TEST7890123"
        })
        package1.write({
            'route_ids': [(6, 0, [route1.id, route2.id])],
        })

        package2 = self.env['freight.package'].create({
            'name': 'Test Package 2',
            'shipment_id': shipment.id,
            'package_type_id': self.container_20gp.id,
            'weight': 15000,
            'volume': 20.0,
            'seal_number': "TEST004",
            'container_number': "TEST4567890"
        })
        package2.write({
            'weight': 15000,
            'volume': 20.0,
            'route_ids': [(6, 0, [route1.id, route2.id])],
        })

        cargo1 = self.env['cargo.commodity'].create({
            'name': 'Test Cargo in Package 1',
            'shipment_id': shipment.id,
            'is_individual_package': True,
            'quantity': 30,
            'package_type_id': self.fiberboard_box.id,
            'weight': 22000,
            'volume': 33.2,
            'cargo_type_id': self.cargo_type_general.id,
            'hs_code_id': self.hs_code_6201.id,
            'country_of_origin_id': self.env.ref('base.vn').id,
        })
        cargo1.write({
            'package_ids': [(4, package1.id)],
        })

        cargo2 = self.env['cargo.commodity'].create({
            'name': 'Test Cargo in Package 2',
            'shipment_id': shipment.id,
            'is_individual_package': True,
            'quantity': 20,
            'package_type_id': self.fiberboard_box.id,
            'weight': 15000,
            'volume': 20.0,
            'cargo_type_id': self.cargo_type_general.id,
            'hs_code_id': self.hs_code_6201.id,
            'country_of_origin_id': self.env.ref('base.vn').id,
        })
        cargo2.write({
            'package_ids': [(4, package2.id)],
            'quantity': 20,
            'weight': 15000,
            'volume': 20.0,
        })

        shipment.action_generate_bookings()

        self.assertEqual(
            len(shipment.booking_ids), 2,
            "Two bookings should be created for routes with different carriers")

        booking_agent = shipment.booking_ids.filtered(
            lambda b: b.carrier_id == self.agent)
        booking_maersk = shipment.booking_ids.filtered(
            lambda b: b.carrier_id == self.maersk_carrier)

        self.assertTrue(
            booking_agent, "Booking with agent carrier should exist")
        self.assertTrue(
            booking_maersk, "Booking with Maersk carrier should exist")

        self.assertEqual(
            len(booking_agent.package_ids), 2,
            "Agent booking should contain both packages")
        self.assertEqual(len(booking_maersk.package_ids), 2,
            "Maersk booking should contain both packages")

        self.assertEqual(len(booking_agent.cargo_commodity_ids), 2,
            "Agent booking should contain cargo from both packages")
        self.assertEqual(
            len(booking_maersk.cargo_commodity_ids), 2,
            "Maersk booking should contain cargo from both packages")

        self.assertEqual(
            len(booking_agent.freight_route_ids), 1,
            "Agent booking should be linked to one route")
        self.assertEqual(
            booking_agent.freight_route_ids.id, route1.id,
            "Agent booking should be linked to route1")
        self.assertEqual(
            len(booking_maersk.freight_route_ids), 1,
            "Maersk booking should be linked to one route")
        self.assertEqual(
            booking_maersk.freight_route_ids.id, route2.id,
            "Maersk booking should be linked to route2")
