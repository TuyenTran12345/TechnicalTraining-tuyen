from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.exceptions import AccessError

from .common import TestCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestAccessRights, cls).setUpClass()
        cls.sale_order_sea_fcl_40ft._action_confirm()
        cls.sale_order_sea_lcl._action_confirm()
        cls.sale_order_land_40ft_fcl._action_confirm()

        cls.admin_shipment = cls.sale_order_sea_fcl_40ft.shipment_ids[:1]
        cls.admin_shipment.write({
            'responsible_id': cls.forwarder_admin.id,
            'carrier_id': cls.maersk_carrier.id,
            'shipper_id': cls.shipper.id,
            'consignee_id': cls.consignee.id,
            'notify_party_id': cls.notify_party.id,
            'house_bill_number': "HBL-20250524-001-VN-DV",
            'etd': fields.Datetime.now(),
            'eta': fields.Datetime.now() + timedelta(days=30),
            'cutoff': fields.Datetime.now() + timedelta(days=-2),
            'stage_ids': [(6, 0, cls.default_shipment_stages.ids)],
        })
        cls.admin_shipment_cargo_template = cls.env['cargo.template'].create({
            'name': "Container 40ft Ready-made Clothing",
            'shipment_id': cls.admin_shipment.id,
            'cargo_template_data_id': cls.container_40ft_t_shirt_cargo_template.id,
            'quantity': 1
        })
        cls.admin_shipment.generator_from_cargo_templates()
        cls.admin_shipment_container_40ft = cls.admin_shipment.package_ids[0]
        cls.admin_shipment_cargo = cls.admin_shipment.cargo_commodity_ids[0]
        cls.admin_shipment.action_generate_bookings()
        cls.admin_booking = cls.admin_shipment.booking_id
        cls.admin_booking.write({
            'responsible_id': cls.forwarder_admin.id,
        })

        cls.user_shipment = cls.sale_order_sea_lcl.shipment_ids[:1]
        cls.user_shipment.write({
            'responsible_id': cls.forwarder_docs.id,
            'carrier_id': cls.maersk_carrier.id,
            'shipper_id': cls.shipper.id,
            'consignee_id': cls.consignee.id,
            'notify_party_id': cls.notify_party.id,
            'house_bill_number': "HBL-20250524-001-VN-DV",
            'etd': fields.Datetime.now(),
            'eta': fields.Datetime.now() + timedelta(days=30),
            'cutoff': fields.Datetime.now() + timedelta(days=-2),
            'stage_ids': [(6, 0, cls.default_shipment_stages.ids)],
        })
        cls.user_shipment_cargo_template = cls.env['cargo.template'].create({
            'name': "Box Ready-made Clothing",
            'shipment_id': cls.user_shipment.id,
            'cargo_template_data_id': cls.container_box_t_shirt_cargo_template.id,
            'quantity': 1
        })
        cls.user_shipment.generator_from_cargo_templates()
        cls.user_shipment_box = cls.user_shipment.package_ids[0]
        cls.user_shipment_cargo = cls.user_shipment.cargo_commodity_ids[0]
        cls.user_shipment.action_generate_bookings()
        cls.user_booking = cls.user_shipment.booking_id
        cls.user_booking.write({
            'responsible_id': cls.forwarder_docs.id,
        })

        cls.non_responsible_shipment = cls.sale_order_land_40ft_fcl.shipment_ids[:1]
        cls.non_responsible_shipment.write({
            'responsible_id': False,
            'carrier_id': cls.maersk_carrier.id,
            'shipper_id': cls.shipper.id,
            'consignee_id': cls.consignee.id,
            'notify_party_id': cls.notify_party.id,
            'house_bill_number': "HBL-20250524-001-VN-DV",
            'etd': fields.Datetime.now(),
            'eta': fields.Datetime.now() + timedelta(days=30),
            'cutoff': fields.Datetime.now() + timedelta(days=-2),
            'stage_ids': [(6, 0, cls.default_shipment_stages.ids)],
        })
        cls.non_responsible_shipment_cargo_template = cls.env['cargo.template'].create({
            'name': "Container 40ft Ready-made Clothing",
            'shipment_id': cls.non_responsible_shipment.id,
            'cargo_template_data_id': cls.container_40ft_t_shirt_cargo_template.id,
            'quantity': 1
        })
        cls.non_responsible_shipment.generator_from_cargo_templates()
        cls.non_responsible_shipment_container_40ft = cls.non_responsible_shipment.package_ids[0]
        cls.non_responsible_shipment_cargo = cls.non_responsible_shipment.cargo_commodity_ids[0]
        cls.non_responsible_shipment.action_generate_bookings()
        cls.non_responsible_booking = cls.non_responsible_shipment.booking_id
        cls.non_responsible_booking.write({
            'responsible_id': False,
        })

        cls.sea_multiple_leg_route_sea_fcl_40ft._action_confirm()
        cls.multiple_leg_route_sea_fcl_40ft = cls.sea_multiple_leg_route_sea_fcl_40ft.shipment_ids[:1]
        cls.multiple_shipment_route_hn_hp = cls.multiple_leg_route_sea_fcl_40ft.freight_route_ids.filtered(lambda r: r.route_id == cls.route_hanoi_hai_phong)
        cls.multiple_shipment_route_dv_usa = cls.multiple_leg_route_sea_fcl_40ft.freight_route_ids.filtered(lambda r: r.route_id == cls.route_dinhvu_usa)
        cls.multiple_leg_route_sea_fcl_40ft.write({
            'responsible_id': cls.forwarder_admin.id,
        })

        cls.fcl_shipment_fcl_single_route.write({'responsible_id': cls.forwarder_admin.id})

    def test_001_freight_user_access_shipment(self):
        """Test Case: Test shipment access rights for Freight Users group
        This group can:
            - access and create all shipments in the system
            - only edit shipment records they are responsible for
        This group cannot:
            - edit shipment records that other employees are responsible for
            - delete any shipment records
        """
        self.user_shipment.with_user(self.forwarder_docs).read(['id'])
        self.user_shipment.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            self.user_shipment.with_user(self.forwarder_docs).unlink()
        self.user_shipment.with_user(self.forwarder_docs).create({'name': 'test'})

        self.non_responsible_shipment.with_user(self.forwarder_docs).read(['id'])
        self.non_responsible_shipment.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            self.non_responsible_shipment.with_user(self.forwarder_docs).unlink()
        self.non_responsible_shipment.with_user(self.forwarder_docs).create({'name': 'test'})

        self.admin_shipment.with_user(self.forwarder_docs).read(['id'])
        with self.assertRaises(AccessError):
            self.admin_shipment.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            self.admin_shipment.with_user(self.forwarder_docs).unlink()

    def test_002_freight_admin_access_shipment(self):
        """Test Case: Test shipment access rights for Freight Admin group
        This group can:
            - have full access to all shipments in the system
        """
        # remove all bookings to avoid error when unlink shipment
        self.admin_shipment.booking_ids.unlink()
        self.user_shipment.booking_ids.unlink()
        self.non_responsible_shipment.booking_ids.unlink()

        self.admin_shipment.with_user(self.forwarder_admin).read(['id'])
        self.admin_shipment.with_user(self.forwarder_admin).write({'name': 'test'})
        self.admin_shipment.with_user(self.forwarder_admin).unlink()
        self.admin_shipment.with_user(self.forwarder_admin).create({'name': 'test', 'responsible_id': self.forwarder_admin.id})

        self.user_shipment.with_user(self.forwarder_admin).read(['id'])
        self.user_shipment.with_user(self.forwarder_admin).write({'name': 'test'})
        self.user_shipment.with_user(self.forwarder_admin).unlink()
        self.user_shipment.with_user(self.forwarder_admin).create({'name': 'test', 'responsible_id': self.forwarder_docs.id})

        self.non_responsible_shipment.with_user(self.forwarder_admin).read(['id'])
        self.non_responsible_shipment.with_user(self.forwarder_admin).write({'name': 'test'})
        self.non_responsible_shipment.with_user(self.forwarder_admin).unlink()
        self.non_responsible_shipment.with_user(self.forwarder_admin).create({'name': 'test', 'responsible_id': False})

    def test_003_freight_user_access_booking(self):
        """Test Case: Test booking access rights for Freight Users group
        This group can:
            - access and create all bookings in the system
            - only edit booking records they are responsible for, or shipments they are responsible for, or shipments with no responsible person
        This group cannot:
            - edit booking records that other employees are responsible for
            - delete any booking records
        """
        self.admin_booking.with_user(self.forwarder_docs).read(['id'])
        with self.assertRaises(AccessError):
            self.admin_booking.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            self.admin_booking.with_user(self.forwarder_docs).unlink()
        with self.assertRaises(AccessError):
            self.env['freight.booking'].with_user(self.forwarder_docs).create({
                'name': 'test',
                'responsible_id': self.forwarder_admin.id,
                'shipment_id': self.admin_shipment.id
            })

        self.user_booking.with_user(self.forwarder_docs).read(['id'])
        self.user_booking.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            self.user_booking.with_user(self.forwarder_docs).unlink()

        self.non_responsible_booking.with_user(self.forwarder_docs).read(['id'])
        self.non_responsible_booking.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            self.non_responsible_booking.with_user(self.forwarder_docs).unlink()

    def test_004_freight_admin_access_booking(self):
        """Test Case: Test booking access rights for Freight Admin group
        This group can:
            - have full access to all bookings in the system
        """
        self.admin_booking.with_user(self.forwarder_admin).read(['id'])
        self.admin_booking.with_user(self.forwarder_admin).write({'name': 'test'})
        self.admin_booking.with_user(self.forwarder_admin).unlink()

        self.user_booking.with_user(self.forwarder_admin).read(['id'])
        self.user_booking.with_user(self.forwarder_admin).write({'name': 'test'})
        self.user_booking.with_user(self.forwarder_admin).unlink()

        self.non_responsible_booking.with_user(self.forwarder_admin).read(['id'])
        self.non_responsible_booking.with_user(self.forwarder_admin).write({'name': 'test'})
        self.non_responsible_booking.with_user(self.forwarder_admin).unlink()

        self.env['freight.booking'].with_user(self.forwarder_admin).name_create('Test')

    def test_005_freight_user_access_package(self):
        """Test Case: Test package access rights for Freight Users group
        This group can:
            - access, create, delete all packages in their own shipments or shipments with no responsible person, or delete packages not linked to any shipment
            - only edit package records in the system they are responsible for
        This group cannot:
            - edit or delete package records that other employees are responsible for
        """
        # Package in other shipment
        self.admin_shipment_container_40ft.with_user(self.forwarder_docs).read(['id'])
        with self.assertRaises(AccessError):
            self.admin_shipment_container_40ft.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            self.admin_shipment_container_40ft.with_user(self.forwarder_docs).unlink()
        with self.assertRaises(AccessError):
            self.env['freight.package'].with_user(self.forwarder_docs).create({
                'name': 'test',
                'package_type_id': self.container_40gp.id,
                'weight': 22000,
                'volume': 33.2,
                'shipment_id': self.admin_shipment.id,
            })

        # Package in own shipment
        self.user_shipment_box.with_user(self.forwarder_docs).read(['id'])
        self.user_shipment_box.with_user(self.forwarder_docs).write({'name': 'test'})
        self.user_shipment_box.with_user(self.forwarder_docs).unlink()
        self.env['freight.package'].with_user(self.forwarder_docs).create({
            'name': 'test',
            'package_type_id': self.container_40gp.id,
            'weight': 22000,
            'volume': 33.2,
            'shipment_id': self.user_shipment.id,
        })

        # Package of shipment with no responsible person
        self.non_responsible_shipment_container_40ft.with_user(self.forwarder_docs).read(['id'])
        self.non_responsible_shipment_container_40ft.with_user(self.forwarder_docs).write({'name': 'test'})
        self.non_responsible_shipment_container_40ft.with_user(self.forwarder_docs).unlink()
        self.env['freight.package'].with_user(self.forwarder_docs).create({
            'name': 'test',
            'package_type_id': self.container_40gp.id,
            'weight': 22000,
            'volume': 33.2,
        })

        # Package not linked to any shipment
        non_shipment_package = self.env['freight.package'].create({
            'name': 'test',
            'package_type_id': self.container_40gp.id,
            'weight': 22000,
            'volume': 33.2,
        })
        non_shipment_package.with_user(self.forwarder_docs).read(['id'])
        non_shipment_package.with_user(self.forwarder_docs).write({'name': 'test'})
        non_shipment_package.with_user(self.forwarder_docs).unlink()

    def test_006_freight_admin_access_package(self):
        """Test Case: Test package access rights for Freight Admin group
        This group can:
            - have full access to all packages in the system
        """
        self.admin_shipment_container_40ft.with_user(self.forwarder_admin).read(['id'])
        self.admin_shipment_container_40ft.with_user(self.forwarder_admin).write({'name': 'test'})
        self.admin_shipment_container_40ft.with_user(self.forwarder_admin).unlink()

        self.user_shipment_box.with_user(self.forwarder_admin).read(['id'])
        self.user_shipment_box.with_user(self.forwarder_admin).write({'name': 'test'})
        self.user_shipment_box.with_user(self.forwarder_admin).unlink()

        self.non_responsible_shipment_container_40ft.with_user(self.forwarder_admin).read(['id'])
        self.non_responsible_shipment_container_40ft.with_user(self.forwarder_admin).write({'name': 'test'})
        self.non_responsible_shipment_container_40ft.with_user(self.forwarder_admin).unlink()

        self.env['freight.package'].with_user(self.forwarder_admin).create({
            'name': 'test',
            'package_type_id': self.container_40gp.id,
        })

    def test_007_freight_user_access_cargo_commodity(self):
        """Test Case: Test cargo commodity access rights for Freight Users group
        This group can:
            - access, create, delete all cargo commodities in their own shipments or shipments with no responsible person, or delete cargo commodities not linked to any shipment
            - only edit cargo commodity records in the system they are responsible for
        This group cannot:
            - edit or delete cargo commodity records that other employees are responsible for
        """
        self.admin_shipment_cargo.with_user(self.forwarder_docs).read(['id'])
        with self.assertRaises(AccessError):
            self.admin_shipment_cargo.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            self.admin_shipment_cargo.with_user(self.forwarder_docs).unlink()
        with self.assertRaises(AccessError):
            self.env['cargo.commodity'].with_user(self.forwarder_docs).create({
                'name': 'test',
                'package_ids': [(4, self.admin_shipment_container_40ft.id)],
                'shipment_id': self.admin_shipment.id,
            })

        self.user_shipment_cargo.with_user(self.forwarder_docs).read(['id'])
        self.user_shipment_cargo.with_user(self.forwarder_docs).write({'name': 'test'})
        self.user_shipment_cargo.with_user(self.forwarder_docs).unlink()
        self.env['cargo.commodity'].with_user(self.forwarder_docs).create({
            'name': 'test',
            'package_ids': [(4, self.user_shipment_box.id)],
            'shipment_id': self.user_shipment.id,
        })

        self.non_responsible_shipment_cargo.with_user(self.forwarder_docs).read(['id'])
        self.non_responsible_shipment_cargo.with_user(self.forwarder_docs).write({'name': 'test'})
        self.non_responsible_shipment_cargo.with_user(self.forwarder_docs).unlink()
        self.env['cargo.commodity'].with_user(self.forwarder_docs).create({
            'name': 'test',
            'package_ids': [(4, self.non_responsible_shipment_container_40ft.id)],
            'shipment_id': self.non_responsible_shipment.id,
        })

        non_shipment_cargo = self.env['cargo.commodity'].create({
            'name': 'test',
            'package_ids': [(4, self.user_shipment_box.id)],
        })
        non_shipment_cargo.with_user(self.forwarder_docs).read(['id'])
        non_shipment_cargo.with_user(self.forwarder_docs).write({'name': 'test'})
        non_shipment_cargo.with_user(self.forwarder_docs).unlink()

    def test_008_freight_user_access_shipment_cargo_template(self):
        """Test Case: Test shipment cargo template access rights for Freight Users group
        This group can:
            - access, create, delete all shipment cargo templates in the system
        This group cannot:
            - edit or delete shipment cargo template records that other employees are responsible for
        """
        self.admin_shipment_cargo_template.with_user(self.forwarder_docs).read(['id'])
        with self.assertRaises(AccessError):
            self.admin_shipment_cargo_template.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            self.admin_shipment_cargo_template.with_user(self.forwarder_docs).unlink()
        with self.assertRaises(AccessError):
            self.env['cargo.template'].with_user(self.forwarder_docs).create({
                'name': 'test',
                'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
                'shipment_id': self.admin_shipment.id,
                'quantity': 1,
            })

        self.user_shipment_cargo_template.with_user(self.forwarder_docs).read(['id'])
        self.user_shipment_cargo_template.with_user(self.forwarder_docs).write({'name': 'test'})
        self.user_shipment_cargo_template.with_user(self.forwarder_docs).unlink()
        self.env['cargo.template'].with_user(self.forwarder_docs).create({
            'name': 'test',
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'shipment_id': self.user_shipment.id,
            'quantity': 1,
        })

        self.non_responsible_shipment_cargo_template.with_user(self.forwarder_docs).read(['id'])
        self.non_responsible_shipment_cargo_template.with_user(self.forwarder_docs).write({'name': 'test'})
        self.non_responsible_shipment_cargo_template.with_user(self.forwarder_docs).unlink()
        self.env['cargo.template'].with_user(self.forwarder_docs).create({
            'name': 'test',
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'shipment_id': self.non_responsible_shipment.id,
            'quantity': 1,
        })

    def test_009_freight_admin_access_shipment_cargo_template(self):
        """Test Case: Test shipment cargo template access rights for Freight Admin group
        This group can:
            - have full access to all shipment cargo templates in the system
        """
        self.admin_shipment_cargo_template.with_user(self.forwarder_admin).read(['id'])
        self.admin_shipment_cargo_template.with_user(self.forwarder_admin).write({'name': 'test'})
        self.admin_shipment_cargo_template.with_user(self.forwarder_admin).unlink()
        self.env['cargo.template'].with_user(self.forwarder_admin).create({
            'name': 'test',
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'shipment_id': self.admin_shipment.id,
            'quantity': 1,
        })

        self.user_shipment_cargo_template.with_user(self.forwarder_admin).read(['id'])
        self.user_shipment_cargo_template.with_user(self.forwarder_admin).write({'name': 'test'})
        self.user_shipment_cargo_template.with_user(self.forwarder_admin).unlink()
        self.env['cargo.template'].with_user(self.forwarder_admin).create({
            'name': 'test',
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'shipment_id': self.user_shipment.id,
            'quantity': 1,
        })

        self.non_responsible_shipment_cargo_template.with_user(self.forwarder_admin).read(['id'])
        self.non_responsible_shipment_cargo_template.with_user(self.forwarder_admin).write({'name': 'test'})
        self.non_responsible_shipment_cargo_template.with_user(self.forwarder_admin).unlink()
        self.env['cargo.template'].with_user(self.forwarder_admin).create({
            'name': 'test',
            'cargo_template_data_id': self.container_40ft_t_shirt_cargo_template.id,
            'shipment_id': self.non_responsible_shipment.id,
            'quantity': 1,
        })

    def test_010_freight_user_access_shipment_leg_route(self):
        """Test Case: Test shipment leg route access rights for Freight Users group
        This group can:
            - access, create, delete all shipment leg routes in the system
        This group cannot:
            - edit or delete shipment leg route records that other employees are responsible for
        """
        self.multiple_shipment_route_hn_hp.with_user(self.forwarder_docs).read(['id'])
        with self.assertRaises(AccessError):
            self.multiple_shipment_route_hn_hp.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            self.multiple_shipment_route_hn_hp.with_user(self.forwarder_docs).unlink()
        with self.assertRaises(AccessError):
            self.env['freight.route'].with_user(self.forwarder_docs).create({
                'name': 'test',
                'shipment_id': self.multiple_leg_route_sea_fcl_40ft.id,
            })

        self.multiple_leg_route_sea_fcl_40ft.write({'responsible_id': self.forwarder_docs.id})
        self.multiple_shipment_route_hn_hp.with_user(self.forwarder_docs).write({'name': 'test'})
        self.multiple_shipment_route_hn_hp.with_user(self.forwarder_docs).unlink()
        self.env['freight.route'].with_user(self.forwarder_docs).create({
            'name': 'test',
            'shipment_id': self.multiple_leg_route_sea_fcl_40ft.id,
        })

        self.multiple_leg_route_sea_fcl_40ft.write({'responsible_id': False})
        self.multiple_shipment_route_dv_usa.with_user(self.forwarder_docs).write({'name': 'test'})
        self.multiple_shipment_route_dv_usa.with_user(self.forwarder_docs).unlink()
        self.env['freight.route'].with_user(self.forwarder_docs).create({
            'name': 'test',
            'shipment_id': self.multiple_leg_route_sea_fcl_40ft.id,
        })

    def test_011_freight_admin_access_shipment_leg_route(self):
        """Test Case: Test shipment leg route access rights for Freight Admin group
        This group can:
            - have full access to all shipment leg routes in the system
        """
        self.multiple_shipment_route_hn_hp.with_user(self.forwarder_admin).read(['id'])
        self.multiple_shipment_route_hn_hp.with_user(self.forwarder_admin).write({'name': 'test'})
        self.multiple_shipment_route_hn_hp.with_user(self.forwarder_admin).unlink()
        new_route = self.env['freight.route'].with_user(self.forwarder_admin).create({
            'name': 'test',
            'shipment_id': self.multiple_leg_route_sea_fcl_40ft.id,
        })

        self.multiple_leg_route_sea_fcl_40ft.write({'responsible_id': self.forwarder_docs.id})
        new_route.with_user(self.forwarder_admin).read(['id'])
        new_route.with_user(self.forwarder_admin).write({'name': 'test path 2'})
        new_route.with_user(self.forwarder_admin).unlink()
        new_route_patch_3 = self.env['freight.route'].with_user(self.forwarder_admin).create({
            'name': 'test path 3',
            'shipment_id': self.multiple_leg_route_sea_fcl_40ft.id,
        })

        self.multiple_leg_route_sea_fcl_40ft.write({'responsible_id': False})
        new_route_patch_3.with_user(self.forwarder_admin).read(['id'])
        new_route_patch_3.with_user(self.forwarder_admin).write({'name': 'test path 4'})
        new_route_patch_3.with_user(self.forwarder_admin).unlink()
        self.env['freight.route'].with_user(self.forwarder_admin).create({
            'name': 'test path 4',
            'shipment_id': self.multiple_leg_route_sea_fcl_40ft.id,
        })

    def test_012_freight_user_access_shipment_tracking(self):
        """Test Case: Test shipment tracking access rights for Freight Users group
        This group can:
            - access, create, edit, delete all tracking of shipments they are responsible for or with no responsible person
        This group cannot:
            - edit or delete shipment tracking records that other employees are responsible for
        """
        self.booking_success_tracking.with_user(self.forwarder_docs).read(['id'])
        with self.assertRaises(AccessError):
            self.booking_success_tracking.with_user(self.forwarder_docs).write({'title_template_id': self.shipment_status_complete.id})
        with self.assertRaises(AccessError):
            self.booking_success_tracking.with_user(self.forwarder_docs).unlink()
        with self.assertRaises(AccessError):
            self.env['freight.shipment.tracking'].with_user(self.forwarder_docs).create({
                'title_template_id': self.shipment_status_complete.id,
                'shipment_id': self.fcl_shipment_fcl_single_route.id,
                'location': 'test',
                'event_time': fields.Datetime.now(),
                'status': 'on_track',
            })

        self.fcl_shipment_fcl_single_route.write({'responsible_id': self.forwarder_docs.id})
        self.booking_success_tracking.with_user(self.forwarder_docs).read(['id'])
        self.booking_success_tracking.with_user(self.forwarder_docs).write({'title_template_id': self.shipment_status_complete.id})
        self.booking_success_tracking.with_user(self.forwarder_docs).unlink()
        self.env['freight.shipment.tracking'].with_user(self.forwarder_docs).create({
            'title_template_id': self.shipment_status_complete.id,
            'shipment_id': self.fcl_shipment_fcl_single_route.id,
            'location': 'test',
            'event_time': fields.Datetime.now(),
            'status': 'on_track',
        })

        self.fcl_shipment_fcl_single_route.write({'responsible_id': False})
        self.pickup_tracking.with_user(self.forwarder_docs).read(['id'])
        self.pickup_tracking.with_user(self.forwarder_docs).write({'title_template_id': self.shipment_status_on_track.id})
        self.pickup_tracking.with_user(self.forwarder_docs).unlink()
        self.env['freight.shipment.tracking'].with_user(self.forwarder_docs).create({
            'title_template_id': self.shipment_status_on_track.id,
            'shipment_id': self.fcl_shipment_fcl_single_route.id,
            'location': 'test',
            'event_time': fields.Datetime.now(),
            'status': 'on_track',
        })

    def test_013_freight_admin_access_shipment_tracking(self):
        """Test Case: Test shipment tracking access rights for Freight Admin group
        This group can:
            - have full access to all shipment tracking in the system
        """
        self.booking_success_tracking.with_user(self.forwarder_admin).read(['id'])
        self.booking_success_tracking.with_user(self.forwarder_admin).write({'title_template_id': self.shipment_status_complete.id})
        self.booking_success_tracking.with_user(self.forwarder_admin).unlink()
        user_booking_success_tracking = self.env['freight.shipment.tracking'].with_user(self.forwarder_admin).create({
            'title_template_id': self.shipment_status_complete.id,
            'shipment_id': self.fcl_shipment_fcl_single_route.id,
            'location': 'test',
            'event_time': fields.Datetime.now(),
            'status': 'on_track',
        })

        self.fcl_shipment_fcl_single_route.write({'responsible_id': self.forwarder_docs.id})
        user_booking_success_tracking.with_user(self.forwarder_docs).read(['id'])
        user_booking_success_tracking.with_user(self.forwarder_docs).write({'title_template_id': self.shipment_status_complete.id})
        user_booking_success_tracking.with_user(self.forwarder_docs).unlink()
        non_user_booking_success_tracking = self.env['freight.shipment.tracking'].with_user(self.forwarder_docs).create({
            'title_template_id': self.shipment_status_complete.id,
            'shipment_id': self.fcl_shipment_fcl_single_route.id,
            'location': 'test',
            'event_time': fields.Datetime.now(),
            'status': 'on_track',
        })

        self.fcl_shipment_fcl_single_route.write({'responsible_id': False})
        non_user_booking_success_tracking.with_user(self.forwarder_admin).read(['id'])
        non_user_booking_success_tracking.with_user(self.forwarder_admin).write({'title_template_id': self.shipment_status_complete.id})
        non_user_booking_success_tracking.with_user(self.forwarder_admin).read(['id'])
        non_user_booking_success_tracking.with_user(self.forwarder_admin).unlink()
        self.env['freight.shipment.tracking'].with_user(self.forwarder_admin).create({
            'title_template_id': self.shipment_status_complete.id,
            'shipment_id': self.fcl_shipment_fcl_single_route.id,
            'location': 'test',
            'event_time': fields.Datetime.now(),
            'status': 'on_track',
        })

    def test_014_freight_user_access_cargo_type(self):
        """Test Case: Test cargo type access rights for Freight Users group
        This group can:
            - access all cargo types in the system
        This group cannot:
            - edit, delete, or create cargo type records
        """
        self.cargo_type_general.with_user(self.forwarder_docs).read(['id'])
        with self.assertRaises(AccessError):
            self.cargo_type_general.with_user(self.forwarder_docs).write({'code': 'test'})
        with self.assertRaises(AccessError):
            self.cargo_type_general.with_user(self.forwarder_docs).unlink()
        with self.assertRaises(AccessError):
            self.env['cargo.type'].with_user(self.forwarder_docs).create({
                'code': 'test',
            })

    def test_015_freight_admin_access_cargo_type(self):
        """Test Case: Test cargo type access rights for Freight Admin group
        This group can:
            - have full access to all cargo types in the system
        """
        self.cargo_type_general.with_user(self.forwarder_admin).read(['id'])
        self.cargo_type_general.with_user(self.forwarder_admin).write({'code': 'test'})
        self.cargo_type_general.with_user(self.forwarder_admin).unlink()
        self.env['cargo.type'].with_user(self.forwarder_admin).create({
            'code': 'test',
        })

    def test_016_freight_user_access_hs_code(self):
        """Test Case: Test HS code access rights for Freight Users group
        This group can:
            - access and create all HS codes in the system
            - edit HS codes they created
        This group cannot:
            - delete HS codes
            - edit HS codes created by others
        """
        self.hs_code_1604.with_user(self.forwarder_docs).read(['id'])
        with self.assertRaises(AccessError):
            self.hs_code_1604.with_user(self.forwarder_docs).write({'code': 'test'})
        with self.assertRaises(AccessError):
            self.hs_code_1604.with_user(self.forwarder_docs).unlink()
        hs_code_test = self.env['hs.code'].with_user(self.forwarder_docs).create({
            'code': 'test',
        })

        hs_code_test.with_user(self.forwarder_docs).read(['id'])
        hs_code_test.with_user(self.forwarder_docs).write({'code': 'test'})
        with self.assertRaises(AccessError):
            hs_code_test.with_user(self.forwarder_docs).unlink()

    def test_017_freight_admin_access_hs_code(self):
        """Test Case: Test HS code access rights for Freight Admin group
        This group can:
            - have full access to all HS codes in the system
        """
        self.hs_code_1604.with_user(self.forwarder_admin).read(['id'])
        self.hs_code_1604.with_user(self.forwarder_admin).write({'code': 'test'})
        self.hs_code_1604.with_user(self.forwarder_admin).unlink()
        self.env['hs.code'].with_user(self.forwarder_admin).create({
            'code': 'test',
        })

    def test_018_freight_user_access_dg_class(self):
        """Test Case: Test dangerous goods class access rights for Freight Users group
        This group can:
            - access all dangerous goods classes in the system
        This group cannot:
            - edit, delete, or create dangerous goods class records
        """
        dg_class = self.explosives
        dg_class.with_user(self.forwarder_docs).read(['id'])
        with self.assertRaises(AccessError):
            dg_class.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            dg_class.with_user(self.forwarder_docs).unlink()
        with self.assertRaises(AccessError):
            self.env['freight.dg.class'].with_user(self.forwarder_docs).create({
                'code': 'test',
                'name': 'test',
                'description': 'test',
            })

    def test_019_freight_admin_access_dg_class(self):
        """Test Case: Test dangerous goods class access rights for Freight Admin group
        This group can:
            - have full access to all dangerous goods classes in the system
        """
        dg_class = self.explosives
        dg_class.with_user(self.forwarder_admin).read(['id'])
        dg_class.with_user(self.forwarder_admin).write({'name': 'test'})
        dg_class.with_user(self.forwarder_admin).unlink()
        self.env['freight.dg.class'].with_user(self.forwarder_admin).create({
            'code': 'test',
            'name': 'test',
            'description': 'test',
        })

    def test_020_freight_user_access_un_number(self):
        """Test Case: Test UN number access rights for Freight Users group
        This group can only read UN number records
        """
        self.un_1203.with_user(self.forwarder_docs).read(['id'])
        with self.assertRaises(AccessError):
            self.un_1203.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            self.un_1203.with_user(self.forwarder_docs).unlink()
        with self.assertRaises(AccessError):
            self.env['freight.un.number'].with_user(self.forwarder_docs).create({
                'name': 'test',
                'dg_class_id': self.explosives.id,
                'proper_shipping_name': 'test',
                'packaging_group': 'i',
                'flash_point': 10,
                'special_provisions': 'test',
            })

    def test_021_freight_admin_access_un_number(self):
        """Test Case: Test UN number access rights for Freight Admin group
        This group can:
            - have full access to all UN numbers in the system
        """
        self.un_1203.with_user(self.forwarder_admin).read(['id'])
        self.un_1203.with_user(self.forwarder_admin).write({'name': 'test'})
        self.un_1203.with_user(self.forwarder_admin).unlink()
        self.env['freight.un.number'].with_user(self.forwarder_admin).create({
            'name': 'test',
            'dg_class_id': self.explosives.id,
            'proper_shipping_name': 'test',
            'packaging_group': 'i',
            'flash_point': 10,
            'special_provisions': 'test',
        })

    def test_022_freight_user_access_shipment_method(self):
        """Test Case: Test shipment method access rights for Freight Users group
        This group can only read shipment method records
        """
        self.shipping_method_fcl.with_user(self.forwarder_docs).read(['id'])
        with self.assertRaises(AccessError):
            self.shipping_method_fcl.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            self.shipping_method_fcl.with_user(self.forwarder_docs).unlink()
        with self.assertRaises(AccessError):
            self.env['freight.shipping.method'].with_user(self.forwarder_docs).create({
                'name': 'test',
            })

    def test_023_freight_admin_access_shipment_method(self):
        """Test Case: Test shipment method access rights for Freight Admin group
        This group can:
            - have full access to all shipment methods in the system
        """
        self.shipping_method_fcl.with_user(self.forwarder_admin).read(['id'])
        self.shipping_method_fcl.with_user(self.forwarder_admin).write({'name': 'test'})
        self.shipping_method_fcl.with_user(self.forwarder_admin).unlink()
        self.env['freight.shipping.method'].with_user(self.forwarder_admin).create({
            'name': 'test',
        })

    def test_024_freight_user_access_shipment_stage(self):
        """Test Case: Test shipment stage access rights for Freight Users group
        This group can only read shipment stage records
        """
        self.shipment_stage_planning.with_user(self.forwarder_docs).read(['id'])
        with self.assertRaises(AccessError):
            self.shipment_stage_planning.with_user(self.forwarder_docs).write({'name': 'test'})
        with self.assertRaises(AccessError):
            self.shipment_stage_planning.with_user(self.forwarder_docs).unlink()
        with self.assertRaises(AccessError):
            self.env['freight.shipment.stage'].with_user(self.forwarder_docs).create({
                'name': 'test',
            })

    def test_025_freight_admin_access_shipment_stage(self):
        """Test Case: Test shipment stage access rights for Freight Admin group
        This group can:
            - have full access to all shipment stages in the system
        """
        self.shipment_stage_planning.with_user(self.forwarder_admin).read(['id'])
        self.shipment_stage_planning.with_user(self.forwarder_admin).write({'name': 'test'})
        self.shipment_stage_planning.with_user(self.forwarder_admin).unlink()
        self.env['freight.shipment.stage'].with_user(self.forwarder_admin).create({
            'name': 'test',
        })
