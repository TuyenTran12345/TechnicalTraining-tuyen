from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestBusiness(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestBusiness, cls).setUpClass()

    def test_01_sea_fcl_single_leg_process(self):
        """Test case for sea FCL single-leg order processing workflow, ensuring smooth and seamless system operation

        Preconditions:
            - Single-leg transport order: sale_order_sea_fcl_40ft

        Steps:
            1. Confirm order: System creates Shipment with the following information:
                - Shipment Type: Sea FCL
                - Shipment Status: Draft
                - Shipment Route: Dinh Vu - USA
                - Shipment Origin: Dinh Vu
                - POL: Dinh Vu Port
                - POD: LA Port - (USA)
                - Shipment Destination: USA
            2. Select Carrier: Maersk, Shipper, Consignee, Notify Party
            3. Fill in House Bill Of Lading number
            4. Set planned dates: ETD/ ETA/ Cutoff
            5. Create Packages: container 40ft
            6. Create Cargo in packages: Ready-made clothing: 120k pieces
            7. Set up transport stages: planned, booking, pickup, in_transit, delivered
            8. Perform Booking: System creates Booking with the following information:
                - Booking Type: Sea FCL
                - Booking Status: Draft
                - Booking Route: Dinh Vu - USA
                - Booking Origin: Dinh Vu
                - POL: Dinh Vu Port
                - POD: LA Port - (USA)
                - Booking Destination: USA
                - Shipment: Shipment created from order
                - Carrier: Maersk
                - Shipper: Shipper
                - Consignee: Consignee
                - Notify Party: Notify Party
                - Booking Date: Current date
                - Estimated time: ETD/ ETA/ Cutoff
                - Package list: container 40ft
                - Cargo list: Ready-made clothing: 120k pieces
            9. Edit Booking information:
                - Vessel name: Maersk Albatross
                - Voyage number: Maersk Albatross - 123456
                - Verify that Shipment information about vessel name and voyage number has been updated
            10. Tracking Shipment:
                - Create first tracking event: booking successful. shipment status changes to `on track`
                - Create second event: vessel delayed 1 day due to storm, update eta, change status to `at risk`, shipment status changes to `at risk`
                - Todo: Check information on external portal
        """
        # Preconditions:
        so_sea_fcl_40ft = self.sale_order_sea_fcl_40ft

        # Steps 1: Confirm order:
        so_sea_fcl_40ft._action_confirm()

        # check shipment information after confirming SO:
        shipment = so_sea_fcl_40ft.shipment_ids[:1]
        self.assertTrue(shipment, "No shipment was generated")
        estimated_shipment_vals = {
            'transport_mode': 'sea',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'route_id': self.route_dinhvu_usa.id,
            'origin_id': self.dinhvu_port.id,
            'port_of_loading_id': self.dinhvu_port.id,
            'port_of_discharge_id': self.la_port.id,
            'destination_id': self.la_port.id,
            'service_type': 'port_to_port',
        }
        actual_shipment_vals = {
            'transport_mode': shipment.transport_mode,
            'ocean_shipping_method_id': shipment.ocean_shipping_method_id.id,
            'route_id': shipment.route_id.id,
            'origin_id': shipment.origin_id.id,
            'port_of_loading_id': shipment.port_of_loading_id.id,
            'port_of_discharge_id': shipment.port_of_discharge_id.id,
            'destination_id': shipment.destination_id.id,
            'service_type': shipment.service_type,
        }
        self.assertEqual(estimated_shipment_vals, actual_shipment_vals, "Expected and actual shipment information after creating SO do not match!")

        # Steps 2 - 3 - 4:
        shipment.write({
            'carrier_id': self.maersk_carrier.id,
            'shipper_id': self.shipper.id,
            'consignee_id': self.consignee.id,
            'notify_party_id': self.notify_party.id,
            'house_bill_number': "HBL-20250524-001-VN-DV",
            'etd': fields.Datetime.now(),
            'eta': fields.Datetime.now() + timedelta(days=30),
            'cutoff': fields.Datetime.now() + timedelta(days=-2),
        })

        # Step 5: Create Packages: container 40ft
        container_40ft = self.env['freight.package'].create({
            'name': "Container 40ft Ready-made Clothing",
            'package_type_id': self.container_40gp.id,
            'weight': 22000,
            'volume': 33.2,
            'shipment_id': shipment.id,
            'seal_number': "00000001",
            'container_number': "MSCU5285725"
        })

        # Step 6: Init Cargo Details in Container 40ft:
        shirt_cargo = self.env['cargo.commodity'].create({
            'package_ids': [(4, container_40ft.id)],
            'shipment_id': shipment.id,
            'name': "Ready-made Clothing",
            'is_individual_package': True,
            'quantity': 30,
            'package_type_id': self.fiberboard_box.id,
            'weight': 22000,
            'volume': 33.2,
            'cargo_type_id': self.cargo_type_general.id,
            'hs_code_id': self.hs_code_6201.id,
            'country_of_origin_id': self.env.ref('base.vn').id,
            'handling_instructions': "Need to be covered with plastic, keep low humidity",
        })

        # Step 7: Set up transport stages
        shipment.write({
            'stage_ids': [(6, 0, self.default_shipment_stages.ids)]
        })

        # Step 8: Perform Booking:
        shipment.action_generate_bookings()
        booking = shipment.booking_id
        estimated_booking_vals = {
            'transport_mode': 'sea',
            'state': 'draft',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'route_id': self.route_dinhvu_usa.id,
            'origin_id': self.dinhvu_port.id,
            'port_of_loading_id': self.dinhvu_port.id,
            'port_of_discharge_id': self.la_port.id,
            'destination_id': self.la_port.id,
            'service_type': 'port_to_port',
            'shipment_id': shipment.id,
            'carrier_id': self.maersk_carrier.id,
            'shipper_id': self.shipper.id,
            'consignee_id': self.consignee.id,
            'notify_party_id': self.notify_party.id,
            'etd': shipment.etd,
            'eta': shipment.eta,
            'cutoff': shipment.cutoff,
            'package_ids': container_40ft.ids,
            'cargo_commodity_ids': shirt_cargo.ids,
        }
        actual_booking_vals = {
            'transport_mode': booking.transport_mode,
            'state': booking.state,
            'ocean_shipping_method_id': booking.ocean_shipping_method_id.id,
            'route_id': booking.route_id.id,
            'origin_id': booking.origin_id.id,
            'port_of_loading_id': booking.port_of_loading_id.id,
            'port_of_discharge_id': booking.port_of_discharge_id.id,
            'destination_id': booking.destination_id.id,
            'service_type': booking.service_type,
            'shipment_id': booking.shipment_id.id,
            'carrier_id': booking.carrier_id.id,
            'shipper_id': booking.shipper_id.id,
            'consignee_id': booking.consignee_id.id,
            'notify_party_id': booking.notify_party_id.id,
            'etd': booking.etd,
            'eta': booking.eta,
            'cutoff': booking.cutoff,
            'package_ids': booking.package_ids.ids,
            'cargo_commodity_ids': booking.cargo_commodity_ids.ids,
        }
        self.assertEqual(estimated_booking_vals, actual_booking_vals, "Expected and actual booking information after creating SO do not match!")

        # Step 9: Edit Booking information:
        booking.write({
            'master_bill_number': "MBL-20250524-001-VN-DV",
            'vessel_name': "Maersk Albatross",
            'vessel_voyage_number': "Maersk Albatross - 123456",
        })
        booking.with_context(bypass_resolution_check=True).action_confirm()
        self.assertEqual(shipment.vessel_name, "Maersk Albatross", "Booking vessel information has not been synchronized to shipment!")
        self.assertEqual(shipment.vessel_voyage_number, "Maersk Albatross - 123456", "Booking voyage number information has not been synchronized to shipment!")

        # Step 10: Tracking Shipment:
        tracking_booking_success = self.env['freight.shipment.tracking'].with_context(default_shipment_id=shipment.id, default_stage_id=shipment.current_stage_id).create({
            'shipment_id': shipment.id,
            'event_time': fields.Datetime.now(),
            'location': 'Hai Phong',
            'title_template_id': self.shipment_status_complete.id,
            'description': "Shipment %s has been booked successfully, vessel name %s, voyage %s, estimated time %s %s" % (shipment.name, shipment.vessel_name, shipment.vessel_voyage_number, shipment.eta, shipment.etd),
        })
        self.assertEqual(shipment.last_tracking_id.id, tracking_booking_success.id, "Failed to automatically update tracking %s as the last tracking of shipment %s" % (tracking_booking_success.title_template_id.name, shipment.name))
        self.assertEqual(shipment.last_tracking_status, 'on_track', "Failed to determine the final status of shipment %s" % (shipment.name))
        self.assertEqual(tracking_booking_success.stage_id, self.shipment_stage_planning)
        shipment.current_stage_id = self.shipment_stage_port_handling.id
        storm_insedent_shipment_tracking = self.env['freight.shipment.tracking'].with_context(default_shipment_id=shipment.id, default_stage_id=shipment.current_stage_id).create({
            'shipment_id': shipment.id,
            'event_time': fields.Datetime.now(),
            'status': 'at_risk',
            'location': 'Hai Phong',
            'title_template_id': self.shipment_status_incident.id,
            'description': "Shipment %s has been delayed 1 day due to storm, estimated arrival time %s" % (shipment.name, shipment.etd + timedelta(days=1)),
            'need_update_shipment_plan': True,
            'transport_mode': 'sea',
            'service_type': 'port_to_port',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'carrier_id': self.maersk_carrier.id,
            'vessel_name': "Maersk Albatross",
            'vessel_voyage_number': "Maersk Albatross - 123456",
            'route_id': self.route_dinhvu_usa.id,
            'origin_id': self.dinhvu_port.id,
            'port_of_loading_id': self.dinhvu_port.id,
            'port_of_discharge_id': self.la_port.id,
            'destination_id': self.la_port.id,
            'etd': shipment.etd + timedelta(days=1),
            'eta': shipment.eta,
            'cutoff': shipment.cutoff,
            'consignee_id': shipment.consignee_id.id,
        })
        self.assertEqual(shipment.last_tracking_id.id, storm_insedent_shipment_tracking.id, "Failed to automatically update tracking %s as the last tracking of shipment %s" % (storm_insedent_shipment_tracking.title_template_id.name, shipment.name))
        self.assertEqual(shipment.last_tracking_status, 'at_risk', "Failed to determine the final status of shipment %s" % (shipment.name))
        self.assertEqual(storm_insedent_shipment_tracking.stage_id, self.shipment_stage_port_handling)

    def test_02_sea_fcl_multi_leg_process(self):
        """Test case for sea FCL multi-leg order processing workflow, ensuring smooth and seamless system operation

        Preconditions:
            - Multi-leg transport order: sea_multiple_leg_route_sea_fcl_40ft

        Steps:
            1. Confirm order: System creates Shipment with the following information:
                - Multiple Leg Route: True
                - Transport Mode: Multiple Mode
                - Route 1: Hanoi - Hai Phong
                    - Route: Hanoi - Hai Phong
                    - Service Type: Port to Port
                    - Transport Mode: Land
                    - Ocean Shipping Method: FCL
                    - Origin: Hanoi
                    - Destination: Hai Phong
                - Route 2: Dinh Vu - LA
                    - Route: Dinh Vu - LA
                    - Service Type: Port to Port
                    - Transport Mode: Sea
                    - Ocean Shipping Method: FCL
                    - Origin: Dinh Vu
                    - Destination: LA
            2. Fill in Shipment information
                - House Bill Of Lading: HBL-20250524-001-VN-DV
                - Direction: Export
                - Container: Container 40ft
                - Cargo in container: 120k ready-made clothing
                - Stage list
            3. Set up information for Shipment routes
                - Route 1: Hanoi - Hai Phong
                    Route type: Pickup
                    Estimated Time: ETA/ ETD/ Cutoff
                    Carrier: 'TTS Logistics'
                    Package list: Container 40ft
                - Route 2: Dinh Vu - LA
                    Route type: Main Carrier
                    Estimated Time: ETA/ ETD/ Cutoff
                    Carrier: 'Maersk'
                    Package list: Container 40ft
            4. Create Booking: System creates 2 Bookings with the following information:
                - Booking 1: Hanoi - Hai Phong
                    - Transport Mode: Land
                    - State: Draft
                    - Land Shipping Method: FCL
                    - Service Type: Port to Port
                    - Shipper: Shipper
                    - Consignee: Consignee
                    - Carrier: TTS Logistics
                    - Notify Party: Notify Party
                    - ETD: ETD of this route
                    - ETA: ETA of this route
                    - Cutoff: Cutoff of this route
                    - Route: Hanoi - Hai Phong
                    - Origin: Hanoi
                    - Port of Loading: Hanoi
                    - Port of Discharge: Hai Phong
                    - Destination: Hai Phong
                    - Package list: Container 40ft
                    - Cargo list: Ready-made clothing: 120k pieces
                - Booking 2: Dinh Vu - LA
                    - Transport Mode: Sea
                    - State: Draft
                    - Ocean Shipping Method: FCL
                    - Service Type: Port to Port
                    - Shipper: Shipper
                    - Consignee: Consignee
                    - Notify Party: Notify Party
                    - Carrier: Maersk
                    - ETD: ETD of this route
                    - ETA: ETA of this route
                    - Cutoff: Cutoff of this route
                    - Route: Dinh Vu - LA
                    - Origin: Dinh Vu
                    - Port of Loading: Dinh Vu
                    - Port of Discharge: LA
                    - Destination: LA
                    - Package list: Container 40ft
                    - Cargo list: Ready-made clothing: 120k pieces
            5. Fill in Booking information, confirm and check Route and Shipment information again
                - Booking 1: Hanoi - Hai Phong
                    - Master Bill Number: MBL-20250524-001-VN-DV
                    - Vehicle Name: 15RM-001
                    - Driver: Scoot
                    - ETA: ETA of this route plus 2 days (due to vehicle arrangement delay)
                    - ETD: ETD of this route plus 2 days
                    - Cutoff: Keep unchanged
                - Booking 2: Dinh Vu - LA
                    - Master Bill Number: MBL-20250524-001-DV-LA
                    - Vehicle Name: Maersk Albatross
                    - Vessel Voyage Number: Maersk Albatross - 123456
                    - ETA: ETA of this route plus 2 days (due to first trip delay)
                    - ETD: ETD of this route plus 2 days (due to first trip delay)
                    - Cutoff: Add 2 days due to first trip delay

                - Check Route 1 information again:
                    - ETD: Add 2 days
                    - ETA: Add 2 days
                    - Cutoff: No change
                    - Vehicle Name: 15RM-001
                    - Driver: Scoot
                - Check Route 2 information again:
                    - ETD: Add 2 days
                    - ETA: Add 2 days
                    - Cutoff: Add 2 days
                    - Vessel Name: Maersk Albatross
                    - Vessel Voyage Number: Maersk Albatross - 123456
                - Check Shipment information again:
                    - Cutoff: Keep unchanged
                    - ETA: Add 2 days
                    - ETD: Add 2 days

            6. Tracking and Update Shipment
                - Create first event: booking successful. shipment status changes to `on track`
                - Create second event:
                    - change shipment stage to cargo receiving
                    - Create tracking notification
                - Create third event:
                    - change shipment stage to in transit
                    - Create tracking
                        - location: Indian Ocean
                        - name: encountered storm
                        - description: due to storm, had to dock at Indian port to avoid storm
                        - status: delayed
                        - need update plan: yes
                        - select route: route 2: DV-LA
                        - estimated time: ETD of route + 3 days
                - Check shipment information:
                    - ETD: delayed by 3 more days
                    - Status: delayed
        """
        # Preconditions:
        multiple_route_so = self.sea_multiple_leg_route_sea_fcl_40ft

        # Steps 1: Confirm order:
        multiple_route_so._action_confirm()
        shipment = multiple_route_so.shipment_ids[:1]
        self.assertTrue(shipment, "No shipment was generated")
        estimated_shipment_vals = {
            'transport_mode': 'multiple',
            'multiple_leg_route': True,
            'route_count': 2,
        }
        actual_shipment_vals = {
            'transport_mode': shipment.transport_mode,
            'multiple_leg_route': shipment.multiple_leg_route,
            'route_count': len(shipment.freight_route_ids),
        }
        hn_hp_route = shipment.freight_route_ids.filtered(lambda r: r.route_id == self.route_hanoi_hai_phong)
        dv_la_route = shipment.freight_route_ids.filtered(lambda r: r.route_id == self.route_dinhvu_usa)
        estimated_hn_hp_route_vals = {
            'origin_id': self.hanoi_air_port.id,
            'destination_id': self.hai_phong_port.id,
            'transport_mode': 'land',
            'service_type': 'port_to_port',
            'land_shipping_method_id': self.shipping_method_fcl.id,
        }
        estimated_dv_la_route_vals = {
            'origin_id': self.dinhvu_port.id,
            'destination_id': self.la_port.id,
            'transport_mode': 'sea',
            'service_type': 'port_to_port',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
        }
        actual_hn_hp_route_vals = {
            'origin_id': hn_hp_route.origin_id.id,
            'destination_id': hn_hp_route.destination_id.id,
            'transport_mode': hn_hp_route.transport_mode,
            'service_type': hn_hp_route.service_type,
            'land_shipping_method_id': hn_hp_route.land_shipping_method_id.id,
        }
        actual_dv_la_route_vals = {
            'origin_id': dv_la_route.origin_id.id,
            'destination_id': dv_la_route.destination_id.id,
            'transport_mode': dv_la_route.transport_mode,
            'service_type': dv_la_route.service_type,
            'ocean_shipping_method_id': dv_la_route.ocean_shipping_method_id.id,
        }

        self.assertEqual(estimated_shipment_vals, actual_shipment_vals, "Expected and actual shipment information after creating SO do not match!")
        self.assertEqual(estimated_hn_hp_route_vals, actual_hn_hp_route_vals, "Expected and actual HN - HP route information do not match!")
        self.assertEqual(estimated_dv_la_route_vals, actual_dv_la_route_vals, "Expected and actual DV - LA route information do not match!")

        # Steps 2: Fill in Shipment information
        shipment.write({
            'house_bill_number': "HBL-20250524-001-VN-DV",
            'direction': 'export',
        })
        container_40ft = self.env['freight.package'].create({
            'name': "Container 40ft Ready-made Clothing",
            'package_type_id': self.container_40gp.id,
            'weight': 22000,
            'volume': 33.2,
            'shipment_id': shipment.id,
            'seal_number': "00000001",
            'container_number': "MSCU5285725"
        })
        ready_made_clothing_cargo = self.env['cargo.commodity'].create({
            'package_ids': [(4, container_40ft.id)],
            'shipment_id': shipment.id,
            'name': "Ready-made Clothing",
            'is_individual_package': True,
            'quantity': 30,
            'package_type_id': self.fiberboard_box.id,
            'weight': 22000,
            'volume': 33.2,
            'cargo_type_id': self.cargo_type_general.id,
            'hs_code_id': self.hs_code_6201.id,
            'country_of_origin_id': self.env.ref('base.vn').id,
            'handling_instructions': "Need to be covered with plastic, keep low humidity",
        })
        shipment.write({
            'stage_ids': [(6, 0, self.default_shipment_stages.ids)]
        })

        # Steps 3: Set up information for Shipment routes
        hn_hp_route.write({
            'package_ids': [(4, container_40ft.id)],
            'eta': fields.Datetime.now() + timedelta(days=3),
            'etd': fields.Datetime.now() + timedelta(days=3),
            'cutoff': fields.Datetime.now() + timedelta(days=2),
            'carrier_id': self.agent.id,
            'route_type': 'pickup',
        })
        dv_la_route.write({
            'package_ids': [(4, container_40ft.id)],
            'etd': fields.Datetime.now() + timedelta(days=5),
            'eta': fields.Datetime.now() + timedelta(days=35),
            'cutoff': fields.Datetime.now() + timedelta(days=4),
            'carrier_id': self.maersk_carrier.id,
            'route_type': 'main_carriage',
        })
        self.assertIn(ready_made_clothing_cargo.id, hn_hp_route.cargo_commodity_ids.ids, "Cargo was not added to HN - HP route")
        self.assertIn(container_40ft.id, dv_la_route.package_ids.ids, "Package was not added to DV - LA route")

        # Steps 4: Create Booking
        shipment.action_generate_bookings()
        self.assertEqual(len(shipment.booking_ids), 2, "Number of generated bookings does not match scenario, expected 2 bookings")
        booking_hn_hp = shipment.booking_ids.filtered(lambda b: b.route_id == self.route_hanoi_hai_phong)
        booking_dv_la = shipment.booking_ids.filtered(lambda b: b.route_id == self.route_dinhvu_usa)
        estimated_booking_hn_hp_vals = {
            'transport_mode': 'land',
            'state': 'draft',
            'land_shipping_method_id': self.shipping_method_fcl.id,
            'route_id': self.route_hanoi_hai_phong.id,
            'origin_id': self.hanoi_air_port.id,
            'port_of_loading_id': self.hanoi_air_port.id,
            'port_of_discharge_id': self.hai_phong_port.id,
            'destination_id': self.hai_phong_port.id,
            'service_type': 'port_to_port',
            'shipment_id': shipment.id,
            'carrier_id': self.agent.id,
            'shipper_id': shipment.shipper_id.id,
            'consignee_id': shipment.consignee_id.id,
            'notify_party_id': hn_hp_route.notify_party_id.id,
            'etd': hn_hp_route.etd,
            'eta': hn_hp_route.eta,
            'cutoff': hn_hp_route.cutoff,
            'package_ids': container_40ft.ids,
            'cargo_commodity_ids': ready_made_clothing_cargo.ids,
        }
        estimated_booking_dv_la_vals = {
            'transport_mode': 'sea',
            'state': 'draft',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'route_id': self.route_dinhvu_usa.id,
            'origin_id': self.dinhvu_port.id,
            'port_of_loading_id': self.dinhvu_port.id,
            'port_of_discharge_id': self.la_port.id,
            'destination_id': self.la_port.id,
            'service_type': 'port_to_port',
            'shipment_id': shipment.id,
            'carrier_id': self.maersk_carrier.id,
            'shipper_id': shipment.shipper_id.id,
            'consignee_id': shipment.consignee_id.id,
            'notify_party_id': dv_la_route.notify_party_id.id,
            'etd': dv_la_route.etd,
            'eta': dv_la_route.eta,
            'cutoff': dv_la_route.cutoff,
            'package_ids': container_40ft.ids,
            'cargo_commodity_ids': ready_made_clothing_cargo.ids,
        }
        actual_booking_hn_hp_vals = {
            'transport_mode': booking_hn_hp.transport_mode,
            'state': booking_hn_hp.state,
            'land_shipping_method_id': booking_hn_hp.land_shipping_method_id.id,
            'route_id': booking_hn_hp.route_id.id,
            'origin_id': booking_hn_hp.origin_id.id,
            'port_of_loading_id': booking_hn_hp.port_of_loading_id.id,
            'port_of_discharge_id': booking_hn_hp.port_of_discharge_id.id,
            'destination_id': booking_hn_hp.destination_id.id,
            'service_type': booking_hn_hp.service_type,
            'shipment_id': booking_hn_hp.shipment_id.id,
            'carrier_id': booking_hn_hp.carrier_id.id,
            'shipper_id': booking_hn_hp.shipper_id.id,
            'consignee_id': booking_hn_hp.consignee_id.id,
            'notify_party_id': booking_hn_hp.notify_party_id.id,
            'etd': booking_hn_hp.etd,
            'eta': booking_hn_hp.eta,
            'cutoff': booking_hn_hp.cutoff,
            'package_ids': booking_hn_hp.package_ids.ids,
            'cargo_commodity_ids': booking_hn_hp.cargo_commodity_ids.ids,
        }
        actual_booking_dv_la_vals = {
            'transport_mode': booking_dv_la.transport_mode,
            'state': booking_dv_la.state,
            'ocean_shipping_method_id': booking_dv_la.ocean_shipping_method_id.id,
            'route_id': booking_dv_la.route_id.id,
            'origin_id': booking_dv_la.origin_id.id,
            'port_of_loading_id': booking_dv_la.port_of_loading_id.id,
            'port_of_discharge_id': booking_dv_la.port_of_discharge_id.id,
            'destination_id': booking_dv_la.destination_id.id,
            'service_type': booking_dv_la.service_type,
            'shipment_id': booking_dv_la.shipment_id.id,
            'carrier_id': booking_dv_la.carrier_id.id,
            'shipper_id': booking_dv_la.shipper_id.id,
            'consignee_id': booking_dv_la.consignee_id.id,
            'notify_party_id': booking_dv_la.notify_party_id.id,
            'etd': booking_dv_la.etd,
            'eta': booking_dv_la.eta,
            'cutoff': booking_dv_la.cutoff,
            'package_ids': booking_dv_la.package_ids.ids,
            'cargo_commodity_ids': booking_dv_la.cargo_commodity_ids.ids,
        }

        self.assertEqual(
            estimated_booking_hn_hp_vals, actual_booking_hn_hp_vals,
            ("Booking route %s generated after shipment %s performed booking does not match expected information" % (booking_hn_hp.name, shipment.name))
        )
        self.assertEqual(
            estimated_booking_dv_la_vals, actual_booking_dv_la_vals,
            ("Booking route %s generated after shipment %s performed booking does not match expected information" % (booking_dv_la.name, shipment.name))
        )

        # Steps 5: Fill in Booking information, confirm and check Route and Shipment information again
        booking_hn_hp.write({
            'master_bill_number': "MBL-20250524-001-VN-DV",
            'truck_name': "15RM-001",
            'driver_id': self.agent.id,
            'eta': hn_hp_route.eta + timedelta(days=2),
            'etd': hn_hp_route.etd + timedelta(days=2),
            'cutoff': hn_hp_route.cutoff,
        })
        booking_dv_la.write({
            'master_bill_number': "MBL-20250524-001-DV-LA",
            'vessel_name': "Maersk Albatross",
            'vessel_voyage_number': "Maersk Albatross - 123456",
            'eta': dv_la_route.eta + timedelta(days=2),
            'etd': dv_la_route.etd + timedelta(days=2),
            'cutoff': dv_la_route.cutoff + timedelta(days=2),
        })
        booking_hn_hp.with_context(bypass_resolution_check=True).action_confirm()
        booking_dv_la.with_context(bypass_resolution_check=True).action_confirm()

        self.assertEqual(hn_hp_route.eta, booking_hn_hp.eta, "ETA of HN - HP route does not match scenario")
        self.assertEqual(hn_hp_route.etd, booking_hn_hp.etd, "ETD of HN - HP route does not match scenario")
        self.assertEqual(hn_hp_route.cutoff, booking_hn_hp.cutoff, "Cutoff of HN - HP route does not match scenario")
        self.assertEqual(dv_la_route.eta, booking_dv_la.eta, "ETA of DV - LA route does not match scenario")
        self.assertEqual(dv_la_route.etd, booking_dv_la.etd, "ETD of DV - LA route does not match scenario")
        self.assertEqual(dv_la_route.cutoff, booking_dv_la.cutoff, "Cutoff of DV - LA route does not match scenario")
        self.assertEqual(shipment.cutoff, booking_hn_hp.cutoff, "Cutoff of shipment does not match scenario")
        self.assertEqual(shipment.eta, booking_dv_la.eta, "ETA of shipment does not match scenario")
        self.assertEqual(shipment.etd, booking_hn_hp.etd, "ETD of shipment does not match scenario")

        # Step 6: Tracking and Update Shipment
        booking_success_tracking = self.env['freight.shipment.tracking'].with_context(default_shipment_id=shipment.id, default_stage_id=shipment.current_stage_id).create({
            'title_template_id': self.shipment_status_complete.id,
            'location': "Hanoi",
            'event_time': fields.Datetime.now() - timedelta(days=2),
            'freight_route_id': hn_hp_route.id,
        })
        self.assertEqual(shipment.last_tracking_id, booking_success_tracking, "Booking update information has not been verified for shipment")
        self.assertEqual(shipment.last_tracking_status, 'on_track', "Shipment status does not match scenario")

        shipment.write({
            'current_stage_id': self.shipment_stage_customs_clearance.id
        })
        hn_hp_route.action_set_in_transit()
        cargo_receiving_tracking = self.env['freight.shipment.tracking'].with_context(default_shipment_id=shipment.id, default_stage_id=shipment.current_stage_id).create({
            'title_template_id': self.shipment_status_on_track.id,
            'location': "Hanoi",
            'event_time': fields.Datetime.now(),
            'freight_route_id': hn_hp_route.id,
        })
        self.assertEqual(shipment.last_tracking_id, cargo_receiving_tracking, "Cargo receiving update information has not been verified for shipment")
        self.assertEqual(shipment.last_tracking_status, 'on_track', "Shipment status does not match scenario")
        self.assertEqual(shipment.atd, hn_hp_route.atd, "ATD of shipment has not been automatically updated when starting the first transport trip")

        hn_hp_route.action_set_done()
        shipment.write({
            'current_stage_id': self.shipment_stage_port_handling.id
        })
        dv_la_route.action_set_in_transit()
        storm_incident_tracking = self.env['freight.shipment.tracking'].with_context(default_shipment_id=shipment.id, default_stage_id=shipment.current_stage_id).create({
            'title_template_id': self.shipment_status_incident.id,
            'location': "Indian Ocean",
            'event_time': fields.Datetime.now(),
            'description': "Due to storm, had to dock at Indian port to avoid storm",
            'status': 'at_risk',
            'freight_route_id': dv_la_route.id,
            'need_update_shipment_plan': True,
            'transport_mode': 'sea',
            'service_type': 'port_to_port',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'carrier_id': self.maersk_carrier.id,
            'vessel_name': "Maersk Albatross",
            'vessel_voyage_number': "Maersk Albatross - 123456",
            'route_id': self.route_dinhvu_usa.id,
            'origin_id': self.dinhvu_port.id,
            'port_of_loading_id': self.dinhvu_port.id,
            'port_of_discharge_id': self.la_port.id,
            'destination_id': self.la_port.id,
            'etd': dv_la_route.etd,
            'eta': dv_la_route.eta + timedelta(days=3),
            'cutoff': dv_la_route.cutoff,
            'consignee_id': dv_la_route.consignee_id.id,
            'notify_party_id': dv_la_route.notify_party_id.id,
        })
        self.assertEqual(shipment.last_tracking_id, storm_incident_tracking, "Storm encounter update information has not been verified for shipment")
        self.assertEqual(shipment.last_tracking_status, 'at_risk', "Shipment status does not match scenario")
        self.assertEqual(shipment.eta, storm_incident_tracking.eta, "ETA of shipment does not match scenario")

    def test_03_add_container_to_booked_shipment(self):
        """Test adding a new container to a shipment with an existing confirmed booking

        Scenario:
        1. Customer asks forwarder to transport a container from DV (Vietnam) to LA (US)
        2. Forwarder creates shipment and booking
        3. Carrier confirms booking
        4. One week before operations, customer needs to add another container
        5. Forwarder adds a new container to the shipment
        6. Forwarder generates a new booking for the new container using the same route and carrier
        7. System should create a separate booking only for the new container

        Expected results:
        - Original booking remains unchanged and confirmed
        - New booking is created only for the new container
        - New booking uses the same route and carrier as the original booking
        """
        shipment = self.env['freight.shipment'].create({
            'name': 'Test Shipment for Additional Container',
            'transport_mode': 'sea',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'route_id': self.route_dinhvu_usa.id,
            'origin_id': self.dinhvu_port.id,
            'port_of_loading_id': self.dinhvu_port.id,
            'port_of_discharge_id': self.la_port.id,
            'destination_id': self.la_port.id,
            'service_type': 'port_to_port',
            'carrier_id': self.maersk_carrier.id,
            'shipper_id': self.shipper.id,
            'consignee_id': self.consignee.id,
            'notify_party_id': self.notify_party.id,
            'house_bill_number': "HBL-20250524-001-VN-DV",
            'etd': fields.Datetime.now() + timedelta(days=7),  # Departure in 1 week
            'eta': fields.Datetime.now() + timedelta(days=37),  # Arrival in 37 days
            'cutoff': fields.Datetime.now() + timedelta(days=5),  # Cutoff in 5 days
        })

        container_1 = self.env['freight.package'].create({
            'name': "First Container 40ft",
            'package_type_id': self.container_40gp.id,
            'weight': 22000,
            'volume': 33.2,
            'shipment_id': shipment.id,
            'seal_number': "SEAL001",
            'container_number': "MSCU1234567"
        })

        self.env['cargo.commodity'].create({
            'package_ids': [(4, container_1.id)],
            'shipment_id': shipment.id,
            'name': "Cargo for First Container",
            'is_individual_package': True,
            'quantity': 1000,
            'package_type_id': self.fiberboard_box.id,
            'weight': 22000,
            'volume': 33.2,
            'cargo_type_id': self.cargo_type_general.id,
            'hs_code_id': self.hs_code_6201.id,
            'country_of_origin_id': self.env.ref('base.vn').id,
        })

        shipment.action_generate_bookings()
        first_booking = shipment.booking_id
        self.assertTrue(first_booking, "First booking should be created")

        first_booking.write({
            'master_bill_number': "MBL-20250524-001-VN-DV",
            'vessel_name': "Maersk Albatross",
            'vessel_voyage_number': "Maersk Albatross - 123456",
        })
        first_booking.action_confirm()

        self.assertEqual(first_booking.state, 'confirmed', "First booking should be confirmed")
        self.assertEqual(container_1.booking_status, 'booked', "First container should be booked")

        container_2 = self.env['freight.package'].create({
            'name': "Second Container 40ft",
            'package_type_id': self.container_40gp.id,
            'weight': 24000,
            'volume': 33.2,
            'shipment_id': shipment.id,
            'seal_number': "SEAL002",
            'container_number': "MSCU7654321"
        })

        cargo_2 = self.env['cargo.commodity'].create({
            'package_ids': [(4, container_2.id)],
            'shipment_id': shipment.id,
            'name': "Cargo for Second Container",
            'is_individual_package': True,
            'quantity': 1200,
            'package_type_id': self.fiberboard_box.id,
            'weight': 24000,
            'volume': 33.2,
            'cargo_type_id': self.cargo_type_general.id,
            'hs_code_id': self.hs_code_6201.id,
            'country_of_origin_id': self.env.ref('base.vn').id,
        })

        self.assertEqual(container_2.booking_status, 'need_booking', "Second container should have booking_status 'need_booking'")

        shipment.action_generate_bookings()

        self.assertEqual(len(shipment.booking_ids), 2, "Shipment should now have two bookings")
        second_booking = shipment.booking_ids.filtered(lambda b: b.id != first_booking.id)
        self.assertTrue(second_booking, "Second booking should be created")

        self.assertEqual(first_booking.state, 'confirmed', "First booking should still be confirmed")
        self.assertEqual(len(first_booking.package_ids), 1, "First booking should still have only one container")
        self.assertEqual(first_booking.package_ids.id, container_1.id, "First booking should be linked to the first container")

        self.assertEqual(len(second_booking.package_ids), 1, "Second booking should have only one container")
        self.assertEqual(second_booking.package_ids.id, container_2.id, "Second booking should be linked to the second container")
        self.assertEqual(second_booking.state, 'draft', "Second booking should be in draft state")

        self.assertEqual(second_booking.carrier_id.id, first_booking.carrier_id.id, "Second booking should use the same carrier as the first booking")
        self.assertEqual(second_booking.route_id.id, first_booking.route_id.id, "Second booking should use the same route as the first booking")

        self.assertEqual(len(second_booking.cargo_commodity_ids), 1, "Second booking should have only one cargo commodity")
        self.assertEqual(second_booking.cargo_commodity_ids.id, cargo_2.id, "Second booking should be linked to the second cargo")

        second_booking.write({
            'master_bill_number': "MBL-20250524-002-VN-DV",
            'vessel_name': "Maersk Albatross",
            'vessel_voyage_number': "Maersk Albatross - 123456",
        })
        second_booking.action_confirm()

        container_1.invalidate_recordset(['booking_status'])
        container_2.invalidate_recordset(['booking_status'])

        self.assertEqual(container_1.booking_status, 'booked', "First container should be booked")
        self.assertEqual(container_2.booking_status, 'booked', "Second container should now be booked")

    def test_04_fill_shipment_data_on_sale_order(self):
        """Test Case: Test fill shipment data on sales order

        When select shipment on sales order, user have to match data between shipment and SO before confirm
        case: single leg route
        """
        so = self.sale_order_sea_lcl
        so_shipment = self.env['freight.shipment'].create({
            'route_id': self.route_dinhvu_usa.id,
            'transport_mode': 'sea',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
        })
        so.shipment_id = so_shipment
        self.assertTrue(so.mismatched_fields_warning, "Shipment must have mismatch warning")
        self.assertIn("Shipping Method", so.mismatched_fields_warning)

        freight_sol = so.order_line.filtered(lambda l: l.product_id.detailed_type == 'freight')
        freight_sol.write({
            'product_id': self.freight_charge_sea_fcl_40ft.id,
        })

        self.assertFalse(so.mismatched_fields_warning, "Shipment must not have mismatch warning")

        so._action_confirm()

    def test_05_multiple_routes_fill_shipment_data_on_sale_order(self):
        """Test Case: Test multiple routes fill shipment data on sales order

        When select shipment on sales order, user have to match data between shipment and SO before confirm
        case: multiple leg route
        """
        so = self.sale_order_land_40ft_fcl
        so_shipment = self.fcl_shipment_fcl_multiple_route
        so.shipment_id = so_shipment

        self.assertTrue(so.mismatched_fields_warning, "Shipment must have mismatch warning")
        self.assertIn("Multiple Leg Route", so.mismatched_fields_warning)

        self.env['sale.order.line'].create({
            'order_id': so.id,
            'product_id': self.freight_charge_sea_fcl_40ft.id,
            'product_uom_qty': 1,
        })

        so._action_confirm()
        self.assertFalse(so.mismatched_fields_warning, "Shipment must not have mismatch warning")

    def test_06_sync_reference_datas_on_sale_order(self):
        """Test Case: Test sync reference datas on sales order

        When select shipment on sales order, user have to match data between shipment and SO before confirm
        if data changes, ie: sale order, sale order line product changes, user have to sync reference datas between shipment and SO
        case: single leg route
        """
        so_shipment = self.env['freight.shipment'].create({
            'transport_mode': 'multiple',
            'multiple_leg_route': True,
            'freight_route_ids': [
                (0, 0, {
                    'route_id': self.route_dinhvu_usa.id,
                    'transport_mode': 'sea',
                    'ocean_shipping_method_id': self.shipping_method_fcl.id,
                }),
                (0, 0, {
                    'route_id': self.route_hanoi_hai_phong.id,
                    'transport_mode': 'land',
                    'land_shipping_method_id': self.shipping_method_fcl.id,
                }),
            ],
        })
        so = self.sale_order_land_40ft_fcl
        so.shipment_id = so_shipment

        self.assertTrue(so.mismatched_fields_warning, "Shipment must have mismatch warning")
        self.assertIn("Multiple Leg Route", so.mismatched_fields_warning)
        so._action_confirm()

        freight_sol_land = so.order_line.filtered(lambda l: l.product_id.detailed_type == 'freight' and l.product_id.transport_mode == 'land')

        land_route = so_shipment.freight_route_ids.filtered(lambda r: r.transport_mode == 'land')
        sea_route = so_shipment.freight_route_ids.filtered(lambda r: r.transport_mode == 'sea')

        self.assertEqual(freight_sol_land.id, land_route.sale_order_line_id.id, "Land route should be mapped to land freight line")
        self.assertFalse(sea_route.sale_order_line_id, "Sea route should not be mapped to sea freight line")

        self.assertNotIn(land_route.route_id.name, so.mismatched_fields_warning)
        self.assertIn(sea_route.route_id.name, so.mismatched_fields_warning)

        # Create additional sea freight line
        freight_sol_sea = self.env['sale.order.line'].create({
            'order_id': so.id,
            'product_id': self.freight_charge_sea_fcl_40ft.id,
            'product_uom_qty': 1,
        })

        so.mapping_to_current_shipment()
        self.assertFalse(so.mismatched_fields_warning, "Shipment must not have mismatch warning")
        # Check both routes have sale_order_line_id assigned

        self.assertEqual(freight_sol_land.id, land_route.sale_order_line_id.id, "Land route should be mapped to land freight line")
        self.assertEqual(freight_sol_sea.id, sea_route.sale_order_line_id.id, "Sea route should be mapped to sea freight line")
