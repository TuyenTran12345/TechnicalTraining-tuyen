from odoo.tests import tagged

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestBusiness(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestBusiness, cls).setUpClass()
        cls.so = cls.sale_order_sea_fcl_40ft
        cls.so._action_confirm()
        cls.shipment = cls.so.shipment_ids[:1]
        cls.package = cls.env['freight.package'].create({
            'name': 'Electronics Container 40ft',
            'package_type_id': cls.container_40gp.id,
            'shipment_id': cls.shipment.id,
            'seal_number': '1234567890',
            'container_number': 'TEAU1234567',
            'cargo_commodity_ids': [(0, 0, {
                'name': 'Air Conditioner',
                'shipment_id': cls.shipment.id,
                'quantity': 100,
                'weight': 10000,
                'volume': 20,
                'cargo_type_id': cls.cargo_type_general.id,
            })]
        })
        cls.cargo_commodity = cls.package.cargo_commodity_ids[:1]

    def test_001_convert_packages_to_template(self):
        """Test Case: Test convert packages to template

        When converting packages to template, must create cargo template data with information from packages
        and return an action dict to redirect to the created template data.
        """
        # Call convert_to_template method which now returns action dict
        action = self.package.convert_to_template()

        # Test 1: Verify action dict structure
        self.assertIsInstance(action, dict, "convert_to_template should return action dict")
        self.assertIn('domain', action, "Action should have domain to filter created records")

        # Test 2: Get created cargo template data using domain
        domain = action['domain']
        res_model = action['res_model']
        self.assertEqual(res_model, 'freight.cargo.template.data', "Action should target cargo template data model")
        cargo_templates = self.env['freight.cargo.template.data'].search(domain)
        self.assertTrue(len(cargo_templates) > 0, "Should create at least one cargo template data")

        # Test 3: Verify created cargo template data
        cargo_template = cargo_templates[0]
        cargo_template_line = cargo_template.cargo_template_data_line_ids[:1]

        cargo_template_expected_vals = {
            'name': 'Electronics Container 40ft' + ' - ' + self.shipment.customer_id.name,
            'packing_mode': 'package',
            'package_type_id': self.package.package_type_id.id,
        }
        cargo_template_line_expected_vals = {
            'name': 'Air Conditioner',
            'quantity': 100,
            'weight': 10000,
            'volume': 20,
            'cargo_type_id': self.cargo_type_general.id,
        }
        cargo_template_actual_vals = {
            'name': cargo_template.name,
            'packing_mode': cargo_template.packing_mode,
            'package_type_id': cargo_template.package_type_id.id,
        }
        cargo_template_line_actual_vals = {
            'name': cargo_template_line.name,
            'quantity': cargo_template_line.quantity,
            'weight': cargo_template_line.weight,
            'volume': cargo_template_line.volume,
            'cargo_type_id': cargo_template_line.cargo_type_id.id,
        }
        self.assertEqual(cargo_template_expected_vals, cargo_template_actual_vals)
        self.assertEqual(cargo_template_line_expected_vals, cargo_template_line_actual_vals)

    def test_002_convert_cargo_to_template(self):
        """Test Case: Test convert cargo to template

        When converting cargo to template, must create cargo template data with information from cargo
        and return an action dict to redirect to the created template data.
        """
        # Call convert_to_template method which now returns action dict
        action = self.cargo_commodity.convert_to_template()

        # Test 1: Verify action dict structure
        self.assertIsInstance(action, dict, "convert_to_template should return action dict")
        self.assertIn('domain', action, "Action should have domain to filter created records")

        # Test 2: Get created cargo template data using domain
        domain = action['domain']
        res_model = action['res_model']
        self.assertEqual(res_model, 'freight.cargo.template.data', "Action should target cargo template data model")
        cargo_templates = self.env['freight.cargo.template.data'].search(domain)
        self.assertTrue(len(cargo_templates) > 0, "Should create at least one cargo template data")

        # Test 3: Verify created cargo template data
        cargo_template = cargo_templates[0]

        cargo_template_expected_vals = {
            'name': self.cargo_commodity.name + ' - ' + self.shipment.customer_id.name,
            'packing_mode': 'bulk',
            'volume': self.cargo_commodity.volume,
            'weight': self.cargo_commodity.weight,
            'cargo_type_id': self.cargo_commodity.cargo_type_id.id,
            'hs_code_id': self.cargo_commodity.hs_code_id.id,
            'country_of_origin_id': self.cargo_commodity.country_of_origin_id.id,
        }
        cargo_template_actual_vals = {
            'name': cargo_template.name,
            'packing_mode': cargo_template.packing_mode,
            'volume': cargo_template.volume,
            'weight': cargo_template.weight,
            'cargo_type_id': cargo_template.cargo_type_id.id,
            'hs_code_id': cargo_template.hs_code_id.id,
            'country_of_origin_id': cargo_template.country_of_origin_id.id,
        }
        self.assertEqual(cargo_template_expected_vals, cargo_template_actual_vals)
