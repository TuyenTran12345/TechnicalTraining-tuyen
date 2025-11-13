from odoo.fields import Command
from odoo.tests import TransactionCase


class TestCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

        cls.env = cls.env(context=dict(no_reset_password=True, tracking_disable=True))

        # ===============================================
        # ================= Process participants ========
        # ===============================================
        # Forwarder: sale, docs, purchase, admin
        cls.forwarder_sale_man = cls.env.ref('base.user_demo')
        cls.forwarder_admin = cls.env.ref('base.user_admin')
        cls.forwarder_docs = cls.env['res.users'].create({
            'name': 'Forwarder Docs',
            'login': 'forwarder_docs',
            'email': 'forwarder_docs@example.viindoo.com',
            'groups_id': [Command.set([cls.env.ref('viin_freight_management.group_freight_user').id])],
        })

        # Customer: customer, shipper, consignee, notify party
        cls.customer = cls.env.ref('base.res_partner_2')
        cls.shipper = cls.env.ref('base.res_partner_2')
        cls.consignee = cls.env.ref('base.res_partner_12')
        cls.notify_party = cls.env.ref('base.res_partner_12')

        # Vendor: agent, carrier, custom declaration
        cls.agent = cls.env.ref('viin_freight_management.res_partner_tts_logistics_demo')
        cls.maersk_carrier = cls.env.ref('viin_freight_management.res_partner_carrier_maersk')
        cls.maersk_carrier_driver = cls.env.ref('viin_freight_management.res_partner_maersk_driver_1')
        cls.one_line_carrier = cls.env.ref('viin_freight_management.res_partner_one_line')
        cls.customer_declaration = cls.env.ref('base.res_partner_3')

        # ===============================================
        # ================= Master Data =================
        # ===============================================

        # Port:
        cls.dinhvu_port = cls.env.ref('viin_freight_management.VNDVU')
        cls.la_port = cls.env.ref('viin_freight_management.USLAX')
        cls.singapore_port = cls.env.ref('viin_freight_management.SGSIN')
        cls.hai_phong_port = cls.env.ref('viin_freight_management.VNHPH')
        cls.hanoi_air_port = cls.env.ref('viin_freight_management.VN_HAN')

        # Route:
        cls.route_dinhvu_usa = cls.env.ref('viin_freight_management.route_dinhvu_usa')
        cls.route_hanoi_singapore = cls.env.ref('viin_freight_management.route_hanoi_singapore')
        cls.route_hanoi_hai_phong = cls.env.ref('viin_freight_management.route_hanoi_hai_phong')

        # Freight Charges
        cls.freight_charge_sea_fcl = cls.env.ref('viin_freight_management.product_template_freight_route_dinhvu_usa_sea_fcl_demo')
        cls.freight_charge_sea_fcl_40ft = cls.env.ref('viin_freight_management.product_variant_freight_route_dinhvu_usa_sea_fcl_40ft_dry_demo')
        cls.freight_charge_sea_lcl = cls.env.ref('viin_freight_management.product_template_freight_route_dinhvu_usa_sea_lcl_demo')
        cls.freight_charge_air_economy = cls.env.ref('viin_freight_management.product_template_freight_route_hanoi_to_singapore_air_economy_demo')
        cls.freight_charge_air_economy_dg = cls.env.ref('viin_freight_management.product_variant_freight_route_hanoi_singapore_air_economy_cargo_dg_demo')
        cls.freight_charge_land_fcl = cls.env.ref('viin_freight_management.product_template_freight_route_hanoi_hai_phong_truck_fcl_demo')
        cls.freight_charge_land_40ft_fcl = cls.env.ref('viin_freight_management.product_variant_freight_route_hn_hp_land_fcl_40ft_dry_demo')

        # Local Charges
        cls.thc_haiphong = cls.env.ref('viin_freight_management.product_template_thc_fcl_haiphong_demo')
        cls.thc_dinhvu = cls.env.ref('viin_freight_management.product_template_thc_fcl_dinhvu_demo')
        cls.thc_dinhvu_container_40ft_hc = cls.env.ref('viin_freight_management.product_variant_thc_dinhvu_container_40ft_hc_demo')
        cls.customs_clearance_haiphong = cls.env.ref('viin_freight_management.product_template_customs_clearance_haiphong_demo')
        cls.customs_clearance_dinhvu = cls.env.ref('viin_freight_management.product_template_customs_clearance_dinhvu_demo')
        cls.clean_container_dv_fee = cls.env.ref('viin_freight_management.product_template_container_cleaning_dinhvu_port_fee_demo')
        cls.doc_fee_charge_dinhvu = cls.env.ref('viin_freight_management.product_template_do_fee_dinhvu_demo')

        # Fee
        cls.ams_fee = cls.env.ref('viin_freight_management.product_template_ams_fee_demo')
        cls.reefer_inspection_fee = cls.env.ref('viin_freight_management.product_template_inspection_dinhvu_fee_demo')

        # Cargo Template Data
        cls.container_40ft_t_shirt_cargo_template = cls.env.ref('viin_freight_management.cargo_template_data_sea_fcl_single_route_demo')
        cls.container_box_t_shirt_cargo_template = cls.env.ref('viin_freight_management.shipment_sea_lcl_order_box_demo')
        cls.rice_cargo_template = cls.env.ref('viin_freight_management.shipment_sea_bulk_rice_order_demo')

        # Shipment Status Template
        cls.shipment_status_complete = cls.env.ref('viin_freight_management.shipment_status_complete')
        cls.shipment_status_on_track = cls.env.ref('viin_freight_management.shipment_status_on_track')
        cls.shipment_status_import_customs_clearance = cls.env.ref('viin_freight_management.shipment_status_import_customs_clearance')
        cls.shipment_status_export_customs_clearance = cls.env.ref('viin_freight_management.shipment_status_export_customs_clearance')
        cls.shipment_status_incident = cls.env.ref('viin_freight_management.shipment_status_incident')

        # Cargo Type
        cls.cargo_type_general = cls.env.ref('viin_freight_management.cargo_type_general')
        cls.cargo_type_refrigerated = cls.env.ref('viin_freight_management.cargo_type_refrigerated')
        cls.cargo_type_dry_bulk = cls.env.ref('viin_freight_management.cargo_type_dry_bulk')
        cls.cargo_type_liquid_bulk = cls.env.ref('viin_freight_management.cargo_type_liquid_bulk')
        cls.cargo_type_hazardous = cls.env.ref('viin_freight_management.cargo_type_hazardous')
        cls.cargo_type_containerized = cls.env.ref('viin_freight_management.cargo_type_containerized')
        cls.cargo_type_project = cls.env.ref('viin_freight_management.cargo_type_project')
        cls.cargo_type_heavy_lift = cls.env.ref('viin_freight_management.cargo_type_heavy_lift')
        cls.cargo_type_oversized = cls.env.ref('viin_freight_management.cargo_type_oversized')
        cls.cargo_type_special = cls.env.ref('viin_freight_management.cargo_type_special')
        cls.cargo_type_livestock = cls.env.ref('viin_freight_management.cargo_type_livestock')
        cls.cargo_type_other = cls.env.ref('viin_freight_management.cargo_type_other')

        # HS Code
        cls.hs_code_1604 = cls.env.ref('viin_freight_management.hs_code_1604')
        cls.hs_code_1006 = cls.env.ref('viin_freight_management.hs_code_1006')
        cls.hs_code_6201 = cls.env.ref('viin_freight_management.hs_code_6201')
        cls.hs_code_7208 = cls.env.ref('viin_freight_management.hs_code_7208')
        cls.hs_code_4016 = cls.env.ref('viin_freight_management.hs_code_4016')
        cls.hs_code_0901 = cls.env.ref('viin_freight_management.hs_code_0901')

        # Shipment Stage
        cls.shipment_stage_planning = cls.env.ref('viin_freight_management.shipment_stage_planning_demo')
        cls.shipment_stage_customs_clearance = cls.env.ref('viin_freight_management.shipment_stage_customs_clearance')
        cls.shipment_stage_port_handling = cls.env.ref('viin_freight_management.shipment_stage_origin_port_handling')
        cls.shipment_stage_international_transport = cls.env.ref('viin_freight_management.shipment_stage_international_transport')
        cls.shipment_stage_destination_port_handling = cls.env.ref('viin_freight_management.shipment_stage_destination_port_handling')
        cls.shipment_stage_domestic_delivery = cls.env.ref('viin_freight_management.shipment_stage_domestic_delivery')
        cls.default_shipment_stages = cls.shipment_stage_planning | cls.shipment_stage_customs_clearance | cls.shipment_stage_port_handling | cls.shipment_stage_international_transport | cls.shipment_stage_destination_port_handling | cls.shipment_stage_domestic_delivery

        # Loading Method
        cls.shipping_method_fcl = cls.env.ref('viin_freight_management.freight_shipping_method_fcl')
        cls.shipping_method_lcl = cls.env.ref('viin_freight_management.freight_shipping_method_lcl')
        cls.shipping_method_bulk = cls.env.ref('viin_freight_management.freight_shipping_method_bulk')
        cls.shipping_method_ftl = cls.env.ref('viin_freight_management.freight_shipping_method_ftl')
        cls.shipping_method_ltl = cls.env.ref('viin_freight_management.freight_shipping_method_ltl')
        cls.shipping_method_project_cargo = cls.env.ref('viin_freight_management.freight_shipping_method_project_cargo')
        cls.shipping_method_express = cls.env.ref('viin_freight_management.freight_shipping_method_express')

        # Package Type
        cls.container_20gp = cls.env.ref('viin_freight_management.stock_package_type_20gp')
        cls.container_40gp = cls.env.ref('viin_freight_management.stock_package_type_40gp')
        cls.container_40hq = cls.env.ref('viin_freight_management.stock_package_type_40hq')
        cls.container_45hq = cls.env.ref('viin_freight_management.stock_package_type_45hq')
        cls.container_20hc = cls.env.ref('viin_freight_management.stock_package_type_20hc')
        cls.container_40ot = cls.env.ref('viin_freight_management.stock_package_type_40ot')
        cls.container_20fr = cls.env.ref('viin_freight_management.stock_package_type_20fr')
        cls.container_40fr = cls.env.ref('viin_freight_management.stock_package_type_40fr')
        cls.container_20reefer = cls.env.ref('viin_freight_management.stock_package_type_20reefer')
        cls.container_40reefer = cls.env.ref('viin_freight_management.stock_package_type_40reefer')
        cls.container_40_hc = cls.env.ref('viin_freight_management.stock_package_type_40_hc')
        cls.container_20tank = cls.env.ref('viin_freight_management.stock_package_type_20tank')
        cls.container_20bulk = cls.env.ref('viin_freight_management.stock_package_type_20bulk')
        cls.container_40pwhc = cls.env.ref('viin_freight_management.stock_package_type_40pwhc')
        cls.truck_3_5 = cls.env.ref('viin_freight_management.stock_package_type_truck_3_5')
        cls.truck_5 = cls.env.ref('viin_freight_management.stock_package_type_truck_5')
        cls.truck_8 = cls.env.ref('viin_freight_management.stock_package_type_truck_8')
        cls.fiberboard_box = cls.env.ref('viin_freight_management.stock_package_fiberboard_box')
        cls.wooden_crate = cls.env.ref('viin_freight_management.stock_package_wooden_crate')
        cls.pallet_euro = cls.env.ref('viin_freight_management.stock_package_pallet_euro')
        cls.drum = cls.env.ref('viin_freight_management.stock_package_drum')

        # DG Class
        cls.explosives = cls.env.ref('viin_freight_management.dg_class_1')
        cls.gases = cls.env.ref('viin_freight_management.dg_class_2')
        cls.flammable_liquids = cls.env.ref('viin_freight_management.dg_class_3')
        cls.flammable_solids = cls.env.ref('viin_freight_management.dg_class_4')
        cls.oxidizing_substances = cls.env.ref('viin_freight_management.dg_class_5')
        cls.organic_peroxides = cls.env.ref('viin_freight_management.dg_class_6')
        cls.toxic_substances = cls.env.ref('viin_freight_management.dg_class_7')
        cls.radioactive_substances = cls.env.ref('viin_freight_management.dg_class_8')
        cls.corrosive_substances = cls.env.ref('viin_freight_management.dg_class_9')

        # Un Number
        cls.un_1203 = cls.env.ref('viin_freight_management.un_number_1203')
        cls.un_1090 = cls.env.ref('viin_freight_management.un_number_1090')
        cls.un_2031 = cls.env.ref('viin_freight_management.un_number_2031')

        # Sale Order
        cls.sale_order_sea_fcl_40ft = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'order_line': [
                Command.create({
                    'product_template_id': cls.freight_charge_sea_fcl.id,
                    'product_id': cls.freight_charge_sea_fcl_40ft.id,
                    'product_uom_qty': 1,
                }),
                Command.create({
                    'product_template_id': cls.thc_dinhvu.id,
                    'product_id': cls.thc_dinhvu_container_40ft_hc.id,
                    'product_uom_qty': 1,
                }),
                Command.create({
                    'product_template_id': cls.ams_fee.id,
                    'product_id': cls.ams_fee.product_variant_id.id,
                    'product_uom_qty': 1,
                }),
                Command.create({
                    'product_template_id': cls.customs_clearance_dinhvu.id,
                    'product_id': cls.customs_clearance_dinhvu.product_variant_id.id,
                    'product_uom_qty': 1,
                    'price_unit': 150,
                }),
                Command.create({
                    'product_template_id': cls.doc_fee_charge_dinhvu.id,
                    'product_id': cls.doc_fee_charge_dinhvu.product_variant_id.id,
                    'product_uom_qty': 1,
                    'price_unit': 200,
                }),
            ]
        })
        cls.sale_order_air_economy = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'order_line': [
                Command.create({
                    'product_template_id': cls.freight_charge_air_economy.id,
                    'product_id': cls.freight_charge_air_economy.product_variant_id.id,
                    'product_uom_qty': 1,
                }),
            ]
        })
        cls.sale_order_sea_lcl = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'order_line': [
                Command.create({
                    'product_template_id': cls.freight_charge_sea_lcl.id,
                    'product_id': cls.freight_charge_sea_lcl.product_variant_id.id,
                    'product_uom_qty': 1,
                }),
                Command.create({
                    'product_template_id': cls.ams_fee.id,
                    'product_id': cls.ams_fee.product_variant_id.id,
                    'product_uom_qty': 1,
                }),
                Command.create({
                    'product_template_id': cls.customs_clearance_dinhvu.id,
                    'product_id': cls.customs_clearance_dinhvu.product_variant_id.id,
                    'product_uom_qty': 1,
                    'price_unit': 20,
                }),
                Command.create({
                    'product_template_id': cls.doc_fee_charge_dinhvu.id,
                    'product_id': cls.doc_fee_charge_dinhvu.product_variant_id.id,
                    'product_uom_qty': 1,
                    'price_unit': 20,
                }),
            ]
        })
        cls.sale_order_land_40ft_fcl = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'order_line': [
                Command.create({
                    'product_id': cls.freight_charge_land_40ft_fcl.id,
                    'product_uom_qty': 1,
                }),
            ]
        })
        cls.sale_order_air_express = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'order_line': [
                Command.create({
                    'product_id': cls.freight_charge_air_economy_dg.id,
                }),
            ]
        })
        cls.sea_multiple_leg_route_sea_fcl_40ft = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'order_line': [
                Command.create({
                    'product_id': cls.freight_charge_land_40ft_fcl.id,
                    'product_uom_qty': 1,
                }),
                Command.create({
                    'product_id': cls.freight_charge_sea_fcl_40ft.id,
                    'product_uom_qty': 1,
                }),
                Command.create({
                    'product_template_id': cls.thc_dinhvu.id,
                    'product_id': cls.thc_dinhvu_container_40ft_hc.id,
                    'product_uom_qty': 1,
                }),
                Command.create({
                    'product_template_id': cls.ams_fee.id,
                    'product_id': cls.ams_fee.product_variant_id.id,
                    'product_uom_qty': 1,
                }),
                Command.create({
                    'product_template_id': cls.customs_clearance_dinhvu.id,
                    'product_id': cls.customs_clearance_dinhvu.product_variant_id.id,
                    'product_uom_qty': 1,
                    'price_unit': 150,
                }),
                Command.create({
                    'product_template_id': cls.doc_fee_charge_dinhvu.id,
                    'product_id': cls.doc_fee_charge_dinhvu.product_variant_id.id,
                    'product_uom_qty': 1,
                    'price_unit': 200,
                }),
            ]
        })

        # Shipment
        cls.fcl_shipment_fcl_single_route = cls.env['freight.shipment'].create({
            'carrier_id': cls.maersk_carrier.id,
            'customer_id': cls.customer.id,
            'responsible_id': cls.forwarder_admin.id,
            'route_id': cls.route_dinhvu_usa.id,
            'transport_mode': 'sea',
            'ocean_shipping_method_id': cls.shipping_method_fcl.id,
        })
        cls.fcl_shipment_fcl_multiple_route = cls.env['freight.shipment'].create({
            'carrier_id': cls.maersk_carrier.id,
            'customer_id': cls.customer.id,
            'responsible_id': cls.forwarder_admin.id,
            'route_id': cls.route_hanoi_hai_phong.id,
            'transport_mode': 'multiple',
            'ocean_shipping_method_id': cls.shipping_method_fcl.id,
            'multiple_leg_route': True,
            'freight_route_ids': [
                Command.create({
                    'route_id': cls.route_hanoi_hai_phong.id,
                    'route_type': 'pickup',
                    'carrier_id': cls.maersk_carrier.id,
                    'transport_mode': 'land',
                    'land_shipping_method_id': cls.shipping_method_fcl.id,
                }),
                Command.create({
                    'route_id': cls.route_dinhvu_usa.id,
                    'route_type': 'delivery',
                    'carrier_id': cls.maersk_carrier.id,
                    'transport_mode': 'sea',
                    'ocean_shipping_method_id': cls.shipping_method_fcl.id,
                }),
            ]
        })
        cls.fcl_shipment_fcl_single_route.write({
            'cargo_mode': 'structured_entry',
        })
        cls.booking_success_tracking = cls.env['freight.shipment.tracking'].create({
            'shipment_id': cls.fcl_shipment_fcl_single_route.id,
            'title_template_id': cls.shipment_status_complete.id,
            'location': 'Dinh Vu - Hai Phong',
            'stage_id': cls.shipment_stage_planning.id,
            'status': 'on_track',
        })
        cls.pickup_tracking = cls.env['freight.shipment.tracking'].create({
            'shipment_id': cls.fcl_shipment_fcl_single_route.id,
            'title_template_id': cls.shipment_status_complete.id,
            'location': 'Deport Dinh Vu',
            'stage_id': cls.shipment_stage_port_handling.id,
            'status': 'on_track',
        })
        cls.container_delivered_tracking = cls.env.ref('viin_freight_management.shipment_tracking_container_delivered_demo')
        cls.vessel_departure_tracking = cls.env.ref('viin_freight_management.shipment_tracking_vessel_departure_demo')
        cls.vessel_arrived_tracking = cls.env.ref('viin_freight_management.shipment_tracking_vessel_arrival_demo')
