from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.exceptions import ValidationError

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestShipmentFeatures(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestShipmentFeatures, cls).setUpClass()

    def test_001_shipment_constraint_multiple_shipments_per_sale_order(self):
        """Test Case: Test constraint that prevents creating multiple shipments for the same sale order

        Each sale order should only be allowed to have one unique shipment to ensure consistency in management.
        """
        # Create sale order and confirm to generate first shipment
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        first_shipment = so.shipment_ids[:1]
        self.assertTrue(first_shipment, "Sale order must generate shipment after confirmation")

        # Try to create second shipment for same sale order - should raise ValidationError
        with self.assertRaises(ValidationError) as context:
            self.env['freight.shipment'].create({
                'name': 'Test Shipment 2',
                'sale_order_id': so.id,
            })

        self.assertIn('Each sales order is created to serve only 1 shipment', str(context.exception))

    def test_002_compute_cargo_totals(self):
        """Test Case: Test compute cargo totals (weight, volume, cargo commodities, packages) ⚖📏

        Shipment must automatically calculate total weight and volume from cargo commodities or packages.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

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

        # Create cargo commodities
        self.env['cargo.commodity'].create({
            'name': 'T-shirts',
            'shipment_id': shipment.id,
            'quantity': 100,
            'weight': 50.0,
            'volume': 2.5,
            'package_ids': [(4, package1.id)],
        })

        self.env['cargo.commodity'].create({
            'name': 'Jeans',
            'shipment_id': shipment.id,
            'quantity': 50,
            'weight': 75.0,
            'volume': 3.0,
            'package_ids': [(4, package2.id)],
        })

        sum_package_weight = package1.weight + package2.weight

        # Check totals calculated from packages (priority over cargo commodities)
        self.assertEqual(shipment.total_packages, 2, "Total packages must equal 2")
        self.assertEqual(sum_package_weight, 125, "Total weight of packages calculated from cargo weight inside must equal 50 + 75 = 125.")
        self.assertEqual(shipment.total_weight, sum_package_weight, "Total weight must equal 125")
        self.assertEqual(shipment.total_volume, 69.5, "Total volume must equal 67.5 + 2.0 = 69.5")

    def test_003_compute_schedule_multiple_legs(self):
        """Test Case: Test compute schedule for multiple leg shipment

        With multiple legs, schedule must be calculated from freight routes.
        """
        so = self.sea_multiple_leg_route_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        # This shipment has multiple leg route
        self.assertTrue(shipment.multiple_leg_route, "Shipment must have multiple leg route")
        self.assertTrue(len(shipment.freight_route_ids) > 1, "Must have more than 1 freight route")

        # Set schedule for routes
        route1 = shipment.freight_route_ids[0]
        route2 = shipment.freight_route_ids[1]

        route1_etd = fields.Datetime.now()
        route1_eta = route1_etd + timedelta(days=3)
        route1_cutoff = route1_etd - timedelta(days=1)

        route2_etd = route1_eta + timedelta(hours=6)
        route2_eta = route2_etd + timedelta(days=25)
        route2_cutoff = route2_etd - timedelta(days=1)

        route1.write({
            'etd': route1_etd,
            'eta': route1_eta,
            'cutoff': route1_cutoff,
        })

        route2.write({
            'etd': route2_etd,
            'eta': route2_eta,
            'cutoff': route2_cutoff,
        })

        # Shipment schedule must be calculated from routes
        self.assertEqual(shipment.etd, route1_etd, "Shipment ETD must equal first route ETD")
        self.assertEqual(shipment.eta, route2_eta, "Shipment ETA must equal last route ETA")
        self.assertEqual(shipment.cutoff, route1_cutoff, "Shipment cutoff must equal earliest cutoff")

    def test_004_compute_transport_mode_icon(self):
        """Test Case: Test compute transport mode icon

        Icon must be set based on transport mode.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        # Test sea transport
        shipment.transport_mode = 'sea'
        self.assertEqual(shipment.transport_mode_icon, 'fa-ship', "Sea transport must have ship icon")

        # Test air transport
        shipment.transport_mode = 'air'
        self.assertEqual(shipment.transport_mode_icon, 'fa-plane', "Air transport must have plane icon")

        # Test land transport
        shipment.transport_mode = 'land'
        self.assertEqual(shipment.transport_mode_icon, 'fa-truck', "Land transport must have truck icon")

        # Test multiple transport
        shipment.write({
            'multiple_leg_route': True,
            'transport_mode': 'multiple',
        })
        self.assertEqual(shipment.transport_mode_icon, 'fa-exchange', "Multiple transport must have exchange icon")

    def test_005_compute_stage_states(self):
        """Test Case: Test compute stage states (is_closed) 🏁

        Shipment must automatically determine closed status based on current stage.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        # Set stages for shipment
        shipment.stage_ids = [(6, 0, self.default_shipment_stages.ids)]

        # Set current stage as planning (not closed)
        shipment.current_stage_id = self.shipment_stage_planning
        self.assertFalse(shipment.is_closed, "Planning stage is not a closed stage")

        # Set current stage as final delivery (closed)
        shipment.current_stage_id = self.shipment_stage_domestic_delivery
        self.assertTrue(shipment.is_closed, "Final delivery stage must be a closed stage")

    def test_006_compute_can_generate_bookings(self):
        """Test Case: Test compute need generate bookings

        Shipment must determine when bookings need to be generated.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        # Create cargo commodities for shipment
        cargo_commodity = self.env['cargo.commodity'].create({
            'name': 'Test Cargo Commodity',
            'shipment_id': shipment.id,
            'quantity': 100,
        })

        # No bookings yet and check cargo commodity is created
        self.assertTrue(cargo_commodity, "Cargo commodity must be created")
        self.assertTrue(shipment.can_generate_bookings, "Shipment with cargo commodities but no bookings must need generation")

        # Create booking
        shipment.action_generate_bookings()

        self.assertFalse(shipment.can_generate_bookings, "Shipment with bookings and cargo commodities no longer needs generation")

    def test_008_compute_display_locations(self):
        """Test Case: Test compute display locations (origin, destination)

        Display locations must show correctly for single and multiple leg.
        """
        # Test single leg
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        if self.dinhvu_port and self.la_port:
            shipment.write({
                'origin_id': self.dinhvu_port.id,
                'destination_id': self.la_port.id,
            })

            self.assertEqual(shipment.display_origin, self.dinhvu_port, "Single leg origin must display correctly")
            self.assertEqual(shipment.display_destination, self.la_port, "Single leg destination must display correctly")

        # Test multiple leg
        so_multi = self.sea_multiple_leg_route_sea_fcl_40ft
        so_multi._action_confirm()
        shipment_multi = so_multi.shipment_ids[:1]

        if shipment_multi.freight_route_ids:
            first_route = shipment_multi.freight_route_ids.sorted('sequence')[0]
            last_route = shipment_multi.freight_route_ids.sorted('sequence')[-1]

            self.assertEqual(shipment_multi.display_origin, first_route.origin_id, "Multiple leg origin must be taken from first route")
            self.assertEqual(shipment_multi.display_destination, last_route.destination_id, "Multiple leg destination must be taken from last route")

    def test_009_compute_display_carrier(self):
        """Test Case: Test compute display carrier

        Display carrier must show correctly for single and multiple leg.
        """
        # Test single leg
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        shipment.carrier_id = self.maersk_carrier
        self.assertEqual(shipment.display_carrier, self.maersk_carrier, "Single leg carrier must display correctly")
        self.assertFalse(shipment.is_multi_carrier, "Single leg is not multi carrier")

        # Test multiple leg with different carriers
        so_multi = self.sea_multiple_leg_route_sea_fcl_40ft
        so_multi._action_confirm()
        shipment_multi = so_multi.shipment_id

        if len(shipment_multi.freight_route_ids) >= 2:
            route1 = shipment_multi.freight_route_ids[0]
            route2 = shipment_multi.freight_route_ids[1]

            if self.agent:
                route1.carrier_id = self.agent
            route2.carrier_id = self.maersk_carrier

            self.assertTrue(shipment_multi.is_multi_carrier, "Multiple leg with different carriers must be multi carrier")

    def test_010_compute_last_tracking_status(self):
        """Test Case: Test compute last tracking status

        Last tracking status must be calculated from the latest tracking.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        # Initially no tracking
        self.assertEqual(shipment.last_tracking_status, 'to_define', "No tracking must be to_define")

        # Create first tracking
        tracking1 = self.env['freight.shipment.tracking'].create({
            'title_template_id': self.shipment_status_complete.id,
            'shipment_id': shipment.id,
            'event_time': fields.Datetime.now() - timedelta(hours=1),
            'status': 'on_track',
        })

        self.assertEqual(shipment.last_tracking_id, tracking1, "Last tracking must be the newly created tracking")
        self.assertEqual(shipment.last_tracking_status, 'on_track', "Status must be synced from tracking")

        # Create second tracking with different status
        tracking2 = self.env['freight.shipment.tracking'].create({
            'title_template_id': self.env['freight.shipment.status.template'].create({'name': 'At Rick'}).id,
            'shipment_id': shipment.id,
            'event_time': fields.Datetime.now(),
            'status': 'at_risk',
        })

        self.assertEqual(shipment.last_tracking_id, tracking2, "Last tracking must be updated")
        self.assertEqual(shipment.last_tracking_status, 'at_risk', "Status must be updated according to new tracking")

    def test_011_generator_from_cargo_templates(self):
        """Test Case: Test generator from cargo templates

        Must generate packages and cargo commodities from cargo template
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        # Create template cargo
        self.env['cargo.template'].create({
            'name': 'Test Cargo Template',
            'shipment_id': shipment.id,
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'quantity': 2,
        })

        # No packages and cargo commodities yet
        self.assertEqual(len(shipment.package_ids), 0, "No packages yet")
        self.assertEqual(len(shipment.cargo_commodity_ids), 0, "No cargo commodities yet")

        # Generate from template cargo
        shipment.generator_from_cargo_templates()

        # Must have packages and cargo commodities created
        self.assertTrue(len(shipment.package_ids) > 0, "Must have packages generated")
        self.assertTrue(len(shipment.cargo_commodity_ids) > 0, "Must have cargo commodities generated")

    def test_012_action_generate_bookings_single_leg(self):
        """Test Case: Test action generate bookings for single leg
        Must generate 1 booking for single leg shipment.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        # Setup shipment info
        shipment.write({
            'carrier_id': self.maersk_carrier.id,
            'shipper_id': self.shipper.id,
            'consignee_id': self.consignee.id,
        })

        # Create cargo commodities
        cargo_commodity = self.env['cargo.commodity'].create({
            'name': 'Test Cargo Commodity',
            'shipment_id': shipment.id,
            'quantity': 100,
        })

        # Generate bookings
        shipment.action_generate_bookings()

        # Must have 1 booking created
        self.assertEqual(len(shipment.booking_ids), 1, "Single leg must have 1 booking")
        booking = shipment.booking_ids[0]
        self.assertEqual(booking.carrier_id, self.maersk_carrier, "Booking must have correct carrier")
        self.assertIn(cargo_commodity.id, booking.cargo_commodity_ids.ids, "Booking must contain shipment cargo commodities")

    def test_013_action_generate_bookings_multiple_legs(self):
        """Test Case: Test action generate bookings for multiple legs

        Must generate multiple bookings for multiple leg shipment.
        """
        so = self.sea_multiple_leg_route_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        # Setup freight routes with carriers
        if len(shipment.freight_route_ids) >= 2:
            route1 = shipment.freight_route_ids[0]
            route2 = shipment.freight_route_ids[1]

            if self.agent:
                route1.carrier_id = self.agent
            route2.carrier_id = self.maersk_carrier

            # Create cargo commodities and assign to routes
            cargo_commodity = self.env['cargo.commodity'].create({
                'name': 'Test Cargo Commodity',
                'shipment_id': shipment.id,
                'quantity': 100,
            })

            route1.cargo_commodity_ids = [(4, cargo_commodity.id)]
            route2.cargo_commodity_ids = [(4, cargo_commodity.id)]

            # Generate bookings
            shipment.action_generate_bookings()

            # Must have multiple bookings created
            self.assertTrue(len(shipment.booking_ids) > 1, "Multiple legs must have multiple bookings")

            # Check carriers of bookings
            carriers = shipment.booking_ids.carrier_id
            if self.agent:
                self.assertIn(self.agent, carriers, "Must have booking with agent carrier")
            self.assertIn(self.maersk_carrier, carriers, "Must have booking with maersk carrier")

    def test_014_shipment_name_sequence(self):
        """Test Case: Test automatic sequence for shipment name

        Shipment name must be generated automatically from sequence.
        """
        shipment = self.env['freight.shipment'].create({
            'transport_mode': 'sea',
        })

        self.assertNotEqual(shipment.name, 'New', "Name must be generated from sequence, not 'New'")
        self.assertTrue(shipment.name.startswith('SHP/'), "Name must start with prefix SHP/")

    def test_015_shipment_third_party_computation(self):
        """Test Case: Test compute third parties

        Third parties must include all related parties.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        shipment.write({
            'shipper_id': self.shipper.id,
            'consignee_id': self.consignee.id,
            'notify_party_id': self.notify_party.id,
            'carrier_id': self.maersk_carrier.id,
        })

        # Only add agent if it exists
        if self.agent:
            shipment.agent_id = self.agent.id

        third_parties = shipment.third_party_ids
        expected_parties = [self.shipper, self.consignee, self.notify_party]
        if self.agent:
            expected_parties.append(self.agent)

        for party in expected_parties:
            if party:
                self.assertIn(party, third_parties, f"Third parties must contain {party.name}")

    def test_016_compute_booking_status_single_leg_shipment(self):
        """Test Case: Test compute booking status for single leg shipment

        Booking status must be calculated from booking state.
        Booking status must be not_booked if no booking is created.
        Booking status must be booking_in_progress if there is at least one booking in progress.
        Booking status must be booked if all bookings are done.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]
        self.assertEqual(shipment.booking_status, 'not_booked', "Booking status must be not_booked if no booking is created")

        self.env['cargo.template'].create({
            'name': 'Test Cargo Template',
            'shipment_id': shipment.id,
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'quantity': 1
        })
        shipment.generator_from_cargo_templates()

        package = shipment.package_ids[0]
        package.write({
            'seal_number': '1234567890',
            'container_number': 'TEAM1234567890',
        })

        shipment.action_generate_bookings()

        self.assertEqual(shipment.booking_status, 'booking_in_progress', "Booking status must be booking_in_progress if there is at least one booking in progress")

        booking = shipment.booking_id
        booking.write({
            'carrier_id': self.maersk_carrier.id,
            'vessel_name': 'Maersk',
            'vessel_voyage_number': '1234567890',
        })
        booking.action_confirm()
        self.assertEqual(shipment.booking_status, 'booking_in_progress', "Booking status must be in progress if bookings not done")

        booking.action_done()
        self.assertEqual(shipment.booking_status, 'booked', "Booking status must be booked if all bookings are done")

    def test_017_compute_booking_status_multiple_legs_shipment(self):
        """Test Case: Test compute booking status for multiple legs shipment

        Booking status must be calculated from booking state.
        Booking status must be not_booked if no booking is created.
        Booking status must be booking_in_progress if there is at least one booking in progress.
        Booking status must be booked if all bookings are done.
        """
        so = self.sea_multiple_leg_route_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]
        self.assertEqual(shipment.booking_status, 'not_booked', "Booking status must be not_booked if no booking is created")

        self.env['cargo.template'].create({
            'name': 'Test Cargo Template',
            'shipment_id': shipment.id,
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'quantity': 1
        })
        shipment.generator_from_cargo_templates()

        packages = shipment.package_ids
        packages.write({
            'seal_number': '1234567890',
            'container_number': 'TEAM1234567890',
        })
        route_hn_hp = shipment.freight_route_ids.filtered(lambda r: r.route_id == self.route_hanoi_hai_phong)
        route_dv_la = shipment.freight_route_ids.filtered(lambda r: r.route_id == self.route_dinhvu_usa)

        route_hn_hp.write({
            'package_ids': [(6, 0, packages.ids)],
            'carrier_id': self.agent.id,
        })
        route_dv_la.write({
            'package_ids': [(6, 0, packages.ids)],
            'carrier_id': self.maersk_carrier.id,
        })

        shipment.action_generate_bookings()
        self.assertEqual(shipment.booking_status, 'booking_in_progress', "Booking status must be booking_in_progress if there is at least one booking in progress")

        booking_hn_hp = route_hn_hp.booking_ids[0]
        booking_dv_usa = route_dv_la.booking_ids[0]

        booking_hn_hp.write({
            'driver_id': self.agent.id,
            'truck_name': 'Truck 1',
        })
        booking_dv_usa.write({
            'carrier_id': self.maersk_carrier.id,
            'vessel_name': 'Maersk',
            'vessel_voyage_number': '1234567890',
        })
        booking_hn_hp.action_confirm()
        booking_dv_usa.action_confirm()
        self.assertEqual(shipment.booking_status, 'booking_in_progress', "Booking status must be booking_in_progress if there is at least one booking in progress")

        booking_hn_hp.action_done()
        self.assertEqual(shipment.booking_status, 'booking_in_progress', "Booking status must be booking_in_progress if there is at least one booking in progress")

        booking_dv_usa.action_done()
        self.assertEqual(shipment.booking_status, 'booked', "Booking status must be booked if all bookings are done")

    def test_018_compute_can_generate_single_leg_shipment_bookings(self):
        """Test Case: Test compute can generate bookings

        Can generate bookings must be calculated from cargo commodities, packages, and bookings.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        self.assertFalse(shipment.can_generate_bookings, "Can generate bookings must be False if there is no cargo commodities or packages")

        self.env['cargo.template'].create({
            'name': 'Test Cargo Template',
            'shipment_id': shipment.id,
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'quantity': 1
        })
        shipment.generator_from_cargo_templates()

        self.assertTrue(shipment.can_generate_bookings, "Can generate bookings must be True if there is cargo commodities or packages")

        shipment.action_generate_bookings()
        self.assertFalse(shipment.can_generate_bookings, "Can generate bookings must be False if there booking was generated")

    def test_019_activity_log_cancel_sale_order(self):
        """Test Case: Test activity log cancel sale order

        Activity log must be created when sale order is cancelled.
        """
        so = self.sale_order_sea_fcl_40ft
        so._action_confirm()
        shipment = so.shipment_ids[:1]

        so._action_cancel()
        self.assertEqual(shipment.last_tracking_status, 'on_hold')
        self.assertEqual(len(shipment.activity_ids), 1, "One activity should be scheduled on the shipment since a SO has been cancelled")

    def test_020_create_sale_order_from_shipment(self):
        """Test Case: Test create sale order from shipment

        Sale order must be created from shipment.
        """
        shipment = self.fcl_shipment_fcl_single_route
        shipment.action_generator_quotation()
        self.assertEqual(len(shipment.sale_order_ids), 1, "Sale order must be created from shipment")
        so = shipment.sale_order_ids[0]
        self.assertEqual(so.partner_id, shipment.customer_id, "Sale order must have correct customer")
        self.assertEqual(so.shipment_id, shipment, "Sale order must have correct shipment")
        self.assertEqual(so.order_line[0].product_id.route_id, shipment.route_id, "Sale order must have correct product route")
        self.assertEqual(so.order_line[0].product_id.transport_mode, shipment.transport_mode, "Sale order must have correct product transport mode")
        self.assertEqual(so.order_line[0].product_id.land_shipping_method_id, shipment.land_shipping_method_id, "Sale order must have correct product land shipping method")

    def test_021_create_sale_order_from_shipment_multiple_legs(self):
        """Test Case: Test create sale order from shipment multiple legs

        Sale order must be created from shipment multiple legs with proper route mapping.
        """
        shipment = self.fcl_shipment_fcl_multiple_route

        shipment_sea = shipment.freight_route_ids.filtered(lambda r: r.transport_mode == 'sea')
        shipment_land = shipment.freight_route_ids.filtered(lambda r: r.transport_mode == 'land')

        self.assertFalse(shipment_sea.sale_order_line_id, "Sea route must not have sale order line")
        self.assertFalse(shipment_land.sale_order_line_id, "Land route must not have sale order line")

        shipment.action_generator_quotation()
        self.assertEqual(len(shipment.sale_order_ids), 1, "Sale order must be created from shipment multiple legs")
        so = shipment.sale_order_ids[0]
        self.assertEqual(so.partner_id, shipment.customer_id, "Sale order must have correct customer")
        self.assertEqual(so.shipment_id, shipment, "Sale order must have correct shipment")
        self.assertEqual(len(so.order_line), 2, "Sale order must have correct number of order lines")

        order_line_sea = so.order_line.filtered(lambda l: l.product_id.transport_mode == 'sea')
        order_line_land = so.order_line.filtered(lambda l: l.product_id.transport_mode == 'land')

        self.assertEqual(shipment_sea.sale_order_line_id, order_line_sea, "Sea sale order line must be mapped to order line sea")
        self.assertEqual(shipment_land.sale_order_line_id, order_line_land, "Land sale order line must be mapped to order line land")

        self.assertEqual(order_line_sea.product_id.route_id, shipment_sea.route_id, "sale order line sea route must be match to sea freight line")
        self.assertEqual(order_line_land.product_id.route_id, shipment_land.route_id, "sale order line land route must be match to land freight line")

        self.assertEqual(order_line_sea.product_id.ocean_shipping_method_id, shipment_sea.ocean_shipping_method_id, "sale order line sea shipping method must be mapped to sea shipment ocean shipping method")
        self.assertEqual(order_line_land.product_id.land_shipping_method_id, shipment_land.land_shipping_method_id, "sale order line land shipping method must be mapped to land shipment land shipping method")
