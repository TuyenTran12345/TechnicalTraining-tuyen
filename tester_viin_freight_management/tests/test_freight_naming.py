from odoo.tests import tagged, Form
from odoo.exceptions import ValidationError

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestFreightNaming(TestCommon):
    """Test suite for freight product naming functionality"""

    @classmethod
    def setUpClass(cls):
        super(TestFreightNaming, cls).setUpClass()

    # ========================================
    # ========== CREATE Method Tests =========
    # ========================================

    def test_001_create_freight_manual_naming_default(self):
        """Test Case: Create freight product with manual naming (default behavior)

        When creating freight product without explicit naming strategy:
        - support_freight_name should default to 'manual'
        - Name should NOT be auto-generated
        """

        freight = self.env['product.template'].create({
            'name': 'Test Freight Service',
            'detailed_type': 'freight',
            'route_id': self.route_dinhvu_usa.id,
            'transport_mode': 'sea',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
        })

        # Assert: Verify manual naming behavior
        self.assertEqual(freight.support_freight_name, 'manual', "Default naming strategy should be 'manual'")
        self.assertEqual(freight.name, 'Test Freight Service', "Should preserve manually provided name")

    def test_002_create_freight_auto_naming_explicit(self):
        """Test Case: Create freight product with explicit auto naming

        When explicitly setting support_freight_name to 'auto':
        - Should respect auto mode
        - Should auto-generate name from components
        """

        freight = self.env['product.template'].create({
            'detailed_type': 'freight',
            'route_id': self.route_dinhvu_usa.id,
            'transport_mode': 'sea',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'support_freight_name': 'auto',
        })

        # Assert: Verify auto naming behavior
        self.assertEqual(freight.support_freight_name, 'auto')
        expected_name = f"[Sea] {self.shipping_method_fcl.name} - {self.route_dinhvu_usa.name}"
        self.assertEqual(freight.name, expected_name, f"Auto-generated name should be '{expected_name}'")

    def test_003_create_non_freight_product(self):
        """Test Case: Create non-freight product should not trigger naming logic"""

        service = self.env['product.template'].create({
            'name': 'Regular Service',
            'detailed_type': 'service',
        })

        self.assertEqual(service.name, 'Regular Service')
        self.assertEqual(service.support_freight_name, 'manual')

    def test_004_create_freight_partial_data_auto_mode(self):
        """Test Case: Create freight with partial data in auto mode should handle gracefully"""

        freight = self.env['product.template'].create({
            'detailed_type': 'freight',
            'route_id': self.route_dinhvu_usa.id,
            'transport_mode': 'air',
            'support_freight_name': 'auto',
        })

        self.assertEqual(freight.support_freight_name, 'auto')
        expected_name = f"[Air] - {self.route_dinhvu_usa.name}"
        self.assertEqual(freight.name, expected_name)

    # ========================================
    # ========== WRITE Method Tests ==========
    # ========================================

    def test_005_write_freight_fields_auto_regeneration(self):
        """Test Case: Writing freight fields should regenerate name in auto mode"""
        freight = self.env['product.template'].create({
            'detailed_type': 'freight',
            'route_id': self.route_dinhvu_usa.id,
            'transport_mode': 'sea',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'support_freight_name': 'auto',
        })
        original_name = freight.name

        freight.write({
            'ocean_shipping_method_id': self.shipping_method_lcl.id,
        })

        self.assertNotEqual(freight.name, original_name,
                            "Name should change when shipping method changes")
        expected_name = f"[Sea] {self.shipping_method_lcl.name} - {self.route_dinhvu_usa.name}"
        self.assertEqual(freight.name, expected_name)

    def test_006_write_name_field_switches_to_manual(self):
        """Test Case: Writing name field directly should switch to manual mode"""
        freight = self.env['product.template'].create({
            'detailed_type': 'freight',
            'route_id': self.route_dinhvu_usa.id,
            'transport_mode': 'sea',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'support_freight_name': 'auto',
        })

        self.assertEqual(freight.support_freight_name, 'auto')

        freight.write({'name': 'My Custom Freight Name'})

        self.assertEqual(freight.support_freight_name, 'manual',
        "Should switch to manual mode when name is directly edited")
        self.assertEqual(freight.name, 'My Custom Freight Name')

    def test_007_write_manual_mode_preserves_name(self):
        """Test Case: Writing fields in manual mode should preserve custom name"""
        freight = self.env['product.template'].create({
            'name': 'Custom Freight Service',
            'detailed_type': 'freight',
            'route_id': self.route_dinhvu_usa.id,
            'transport_mode': 'sea',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'support_freight_name': 'manual',
        })

        freight.write({
            'transport_mode': 'air',
            'ocean_shipping_method_id': False,
            'air_shipping_method_id': self.shipping_method_express.id,
        })

        self.assertEqual(freight.name, 'Custom Freight Service',
            "Manual name should be preserved when fields change")

    def test_008_write_bulk_freight_records_auto_mode(self):
        """Test Case: Bulk write operations should handle multiple records correctly in auto mode"""
        freights = self.env['product.template'].create([
            {
                'detailed_type': 'freight',
                'route_id': self.route_dinhvu_usa.id,
                'transport_mode': 'sea',
                'ocean_shipping_method_id': self.shipping_method_fcl.id,
                'support_freight_name': 'auto',
            },
            {
                'detailed_type': 'freight',
                'route_id': self.route_hanoi_singapore.id,
                'transport_mode': 'air',
                'air_shipping_method_id': self.shipping_method_express.id,
                'support_freight_name': 'auto',
            }
        ])

        new_route = self.route_hanoi_hai_phong
        freights.write({'route_id': new_route.id})

        for freight in freights:
            self.assertEqual(freight.support_freight_name, 'auto')
            self.assertIn(new_route.name, freight.name,
                f"Route name should be updated in freight: {freight.name}")

    # ========================================
    # ========== ONCHANGE Tests =============
    # ========================================

    def test_009_onchange_detailed_type_to_freight_no_context(self):
        """Test Case: Changing detailed_type to freight without context keeps manual"""
        with Form(self.env['product.template']) as form:
            form.name = 'Test Product'
            form.detailed_type = 'service'

            form.detailed_type = 'freight'
            form.route_id = self.route_dinhvu_usa
            form.transport_mode = 'sea'
            form.ocean_shipping_method_id = self.shipping_method_fcl

            self.assertEqual(form.support_freight_name, 'manual',
                "Should stay manual when no context suggests auto")

    def test_009b_form_with_freight_menu_context(self):
        """Test Case: Creating freight via menu action should have proper defaults"""
        freight_context = {
            'default_detailed_type': 'freight',
            'default_support_freight_name': 'auto',
        }

        with Form(self.env['product.template'].with_context(**freight_context)) as form:
            form.route_id = self.route_dinhvu_usa
            form.transport_mode = 'sea'
            form.ocean_shipping_method_id = self.shipping_method_fcl

            self.assertEqual(form.detailed_type, 'freight',
                "Should default to freight from context")
            self.assertEqual(form.support_freight_name, 'auto', "Should default to auto from context")
            expected_name = f"[Sea] {self.shipping_method_fcl.name} - {self.route_dinhvu_usa.name}"
            self.assertEqual(form.name, expected_name)

    def test_009c_onchange_with_freight_context(self):
        """Test Case: Changing to freight with menu context should trigger auto mode"""
        freight_context = {
            'default_support_freight_name': 'auto',
        }

        with Form(self.env['product.template'].with_context(**freight_context)) as form:
            form.name = 'Test Product'
            form.detailed_type = 'service'

            form.detailed_type = 'freight'
            form.route_id = self.route_dinhvu_usa
            form.transport_mode = 'sea'
            form.ocean_shipping_method_id = self.shipping_method_fcl

            self.assertEqual(form.support_freight_name, 'auto', "Should switch to auto when context suggests it")

    def test_010_onchange_detailed_type_from_freight(self):
        """Test Case: Changing away from freight should clear freight fields"""
        freight_context = {
            'default_detailed_type': 'freight',
            'default_support_freight_name': 'auto',
        }

        with Form(self.env['product.template'].with_context(**freight_context)) as form:
            form.route_id = self.route_dinhvu_usa
            form.transport_mode = 'sea'
            form.ocean_shipping_method_id = self.shipping_method_fcl

            form.detailed_type = 'service'

            self.assertEqual(form.support_freight_name, 'manual')
            self.assertFalse(form.route_id)
            self.assertFalse(form.transport_mode)

    def test_011_onchange_freight_fields_live_preview(self):
        """Test Case: Changing freight fields should update name live in auto mode"""
        freight_context = {
            'default_detailed_type': 'freight',
            'default_support_freight_name': 'auto',
        }

        with Form(self.env['product.template'].with_context(**freight_context)) as form:
            form.route_id = self.route_dinhvu_usa
            form.transport_mode = 'sea'
            form.ocean_shipping_method_id = self.shipping_method_fcl

            initial_name = form.name

            form.ocean_shipping_method_id = self.shipping_method_lcl

            self.assertNotEqual(form.name, initial_name,
                                "Name should update when shipping method changes")
            self.assertIn(self.shipping_method_lcl.name, form.name)

    def test_012_onchange_manual_name_edit_switches_mode(self):
        """Test Case: Manually editing name should switch to manual mode"""
        freight_context = {
            'default_detailed_type': 'freight',
            'default_support_freight_name': 'auto',
        }

        with Form(self.env['product.template'].with_context(**freight_context)) as form:
            form.route_id = self.route_dinhvu_usa
            form.transport_mode = 'sea'
            form.ocean_shipping_method_id = self.shipping_method_fcl

            self.assertEqual(form.support_freight_name, 'auto')

            form.name = 'My Custom Freight Service'

            self.assertEqual(form.support_freight_name, 'manual',
                "Should switch to manual mode when name is manually edited")

    def test_012b_context_vs_no_context_comparison(self):
        """Test Case: Compare form behavior with and without menu context"""
        with Form(self.env['product.template']) as form_no_context:
            form_no_context.name = 'Manual Freight Service'
            form_no_context.detailed_type = 'freight'
            form_no_context.route_id = self.route_dinhvu_usa
            form_no_context.transport_mode = 'sea'
            form_no_context.ocean_shipping_method_id = self.shipping_method_fcl

            self.assertEqual(form_no_context.support_freight_name, 'manual')
            no_context_name = form_no_context.name

        freight_context = {
            'default_detailed_type': 'freight',
            'default_support_freight_name': 'auto',
        }
        with Form(self.env['product.template'].with_context(**freight_context)) as form_with_context:
            form_with_context.route_id = self.route_dinhvu_usa
            form_with_context.transport_mode = 'sea'
            form_with_context.ocean_shipping_method_id = self.shipping_method_fcl

            self.assertEqual(form_with_context.support_freight_name, 'auto')
            with_context_name = form_with_context.name

        self.assertNotEqual(no_context_name, with_context_name,
                            "Context vs no-context should produce different results")

        self.assertEqual(no_context_name, 'Manual Freight Service')

        self.assertIn('[Sea]', with_context_name)
        self.assertIn(self.shipping_method_fcl.name, with_context_name)

    def test_013_onchange_manual_mode_no_auto_update(self):
        """Test Case: Fields changes in manual mode should not update name"""
        with Form(self.env['product.template']) as form:
            form.detailed_type = 'freight'
            form.support_freight_name = 'manual'
            form.name = 'Custom Freight Name'
            form.route_id = self.route_dinhvu_usa
            form.transport_mode = 'sea'
            form.ocean_shipping_method_id = self.shipping_method_fcl

            form.transport_mode = 'air'
            form.air_shipping_method_id = self.shipping_method_express

            self.assertEqual(form.name, 'Custom Freight Name', "Manual name should not change when fields update")

    # ========================================
    # =========== Core Logic Tests ===========
    # ========================================

    def test_014_build_freight_name_all_components(self):
        """Test Case: Name building with all components present in auto mode"""
        freight = self.env['product.template'].create({
            'detailed_type': 'freight',
            'route_id': self.route_dinhvu_usa.id,
            'transport_mode': 'sea',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'support_freight_name': 'auto',
        })

        expected_pattern = f"[Sea] {self.shipping_method_fcl.name} - {self.route_dinhvu_usa.name}"
        self.assertEqual(freight.name, expected_pattern)

    def test_015_build_freight_name_missing_components(self):
        """Test Case: Name building with missing components should handle gracefully"""
        freight_route_only = self.env['product.template'].create({
            'detailed_type': 'freight',
            'route_id': self.route_dinhvu_usa.id,
            'support_freight_name': 'auto',
        })
        self.assertEqual(freight_route_only.name, self.route_dinhvu_usa.name)

        freight_mode_only = self.env['product.template'].create({
            'detailed_type': 'freight',
            'transport_mode': 'sea',
            'route_id': self.route_dinhvu_usa.id,
            'support_freight_name': 'auto',
        })
        expected_name = f"[Sea] - {self.route_dinhvu_usa.name}"
        self.assertEqual(freight_mode_only.name, expected_name)

    def test_016_transport_mode_shipping_method_priority(self):
        """Test Case: Shipping method selection should prioritize mode-specific method"""
        freight = self.env['product.template'].create({
            'detailed_type': 'freight',
            'support_freight_name': 'auto',
            'route_id': self.route_dinhvu_usa.id,
            'transport_mode': 'sea',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
            'air_shipping_method_id': self.shipping_method_express.id,
        })

        self.assertIn(self.shipping_method_fcl.name, freight.name)
        self.assertNotIn(self.shipping_method_express.name, freight.name)

    def test_017_context_skip_autoname_prevention(self):
        """Test Case: Context skip_autoname should prevent infinite loops"""
        freight = self.env['product.template'].create({
            'detailed_type': 'freight',
            'support_freight_name': 'auto',
            'route_id': self.route_dinhvu_usa.id,
            'transport_mode': 'sea',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
        })

        original_name = freight.name

        freight.with_context(skip_autoname=True).write({
            'transport_mode': 'air',
            'ocean_shipping_method_id': False,
            'air_shipping_method_id': self.shipping_method_express.id,
        })

        self.assertEqual(freight.name, original_name, "Name should not change when skip_autoname=True")

    # ========================================
    # === Edge Cases and Error Handling ======
    # ========================================

    def test_018_freight_constraint_validation(self):
        """Test Case: Freight products should require route"""
        with self.assertRaises(ValidationError):
            self.env['product.template'].create({
                'name': 'Test Freight',
                'detailed_type': 'freight',
                'transport_mode': 'sea',

            })

    def test_019_local_charge_vs_freight_naming(self):
        """Test Case: Local charge products should not use freight naming"""
        local_charge = self.env['product.template'].create({
            'name': 'THC Fee',
            'detailed_type': 'local_charge',
            'port_id': self.hai_phong_port.id,
        })

        self.assertEqual(local_charge.name, f'THC Fee - {self.hai_phong_port.ref} ({self.hai_phong_port.country_id.code})')
        self.assertEqual(local_charge.support_freight_name, 'manual')

    def test_020_mixed_detailed_type_bulk_operations(self):
        """Test Case: Bulk operations on mixed product types should handle correctly"""
        products = self.env['product.template'].create([
            {
                'name': 'Regular Service',
                'detailed_type': 'service',
            },
            {
                'detailed_type': 'freight',
                'support_freight_name': 'auto',
                'route_id': self.route_dinhvu_usa.id,
                'transport_mode': 'sea',
                'ocean_shipping_method_id': self.shipping_method_fcl.id,
            },
            {
                'name': 'THC Fee',
                'detailed_type': 'local_charge',
                'port_id': self.hai_phong_port.id,
            }
        ])

        service = products.filtered(lambda p: p.detailed_type == 'service')
        freight = products.filtered(lambda p: p.detailed_type == 'freight')
        local_charge = products.filtered(
            lambda p: p.detailed_type == 'local_charge')

        self.assertEqual(service.name, 'Regular Service')
        self.assertIn('[Sea]', freight.name)
        self.assertEqual(local_charge.name, f'THC Fee - {self.hai_phong_port.ref} ({self.hai_phong_port.country_id.code})')

    # ========================================
    # === Integration and Performance Tests ==
    # ========================================

    def test_021_large_batch_create_performance(self):
        """Test Case: Creating large batch of freight products should be efficient"""
        freight_data = []
        routes = [self.route_dinhvu_usa, self.route_hanoi_singapore, self.route_hanoi_hai_phong]
        methods = [self.shipping_method_fcl, self.shipping_method_lcl]

        for i in range(50):
            freight_data.append({
                'detailed_type': 'freight',
                'support_freight_name': 'auto',
                'route_id': routes[i % len(routes)].id,
                'transport_mode': 'sea',
                'ocean_shipping_method_id': methods[i % len(methods)].id,
            })

        freights = self.env['product.template'].create(freight_data)

        self.assertEqual(len(freights), 50)
        for freight in freights:
            self.assertEqual(freight.support_freight_name, 'auto')
            self.assertIn('[Sea]', freight.name)
            self.assertNotEqual(freight.name, 'Freight')

    def test_022_switching_modes_preserves_user_intent(self):
        """Test Case: Complex scenario with mode switching should preserve user intent"""
        with Form(self.env['product.template']) as form:
            form.detailed_type = 'freight'
            form.route_id = self.route_dinhvu_usa
            form.transport_mode = 'sea'
            form.ocean_shipping_method_id = self.shipping_method_fcl

            form.name = 'Premium Sea Freight Service'
            self.assertEqual(form.support_freight_name, 'manual')

            form.transport_mode = 'air'
            form.air_shipping_method_id = self.shipping_method_express

            self.assertEqual(form.name, 'Premium Sea Freight Service')

            form.support_freight_name = 'auto'

            self.assertNotEqual(form.name, 'Premium Sea Freight Service')
            self.assertIn('[Air]', form.name)
            self.assertIn(self.shipping_method_express.name, form.name)

    def test_023_display_name_display_with_port(self):
        """Test Case: display_name should display port for local charges"""
        freight = self.env['product.template'].create({
            'detailed_type': 'freight',
            'support_freight_name': 'auto',
            'route_id': self.route_dinhvu_usa.id,
            'transport_mode': 'sea',
            'ocean_shipping_method_id': self.shipping_method_fcl.id,
        })

        freight_display = freight.display_name
        self.assertEqual(freight_display, freight.name)

        local_charge = self.env['product.template'].create({
            'name': 'THC Fee',
            'detailed_type': 'local_charge',
            'port_id': self.hai_phong_port.id,
        })

        local_charge_display = local_charge.display_name
        expected_display = f"THC Fee - {self.hai_phong_port.ref} ({self.hai_phong_port.country_id.code})"
        self.assertEqual(local_charge_display, expected_display)
