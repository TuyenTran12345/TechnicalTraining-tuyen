from odoo import models, fields


class UNNumber(models.Model):
    _name = 'freight.un.number'
    _description = 'UN Number'
    _rec_name = 'name'

    name = fields.Char(string='UN Number', required=True, help="Unique UN Number for Dangerous Goods (e.g., UN 1203, UN 1075)")
    proper_shipping_name = fields.Char(string='Proper Shipping Name', required=True, help="Official name for transport (e.g., Gasoline, Acetone)")
    dg_class_id = fields.Many2one('freight.dg.class', string='DG Class', required=True, help="Related Dangerous Goods Class")

    packaging_group = fields.Selection([
        ('i', 'PG I - High Danger'),
        ('ii', 'PG II - Medium Danger'),
        ('iii', 'PG III - Low Danger')
    ], string='Packaging Group', help="Packaging requirement based on the UN classification")

    flash_point = fields.Float(string='Flash Point (°C)', help="Flash point temperature in degrees Celsius")
    special_provisions = fields.Text(string='Special Provisions', help="Special handling, storage, or transport restrictions")

    active = fields.Boolean(string='Active', default=True)
