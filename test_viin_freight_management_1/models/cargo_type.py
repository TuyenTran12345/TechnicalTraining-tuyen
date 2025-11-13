from odoo import models, fields, api


class CargoType(models.Model):
    _name = 'cargo.type'
    _description = 'Cargo Type'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True, help="Unique code for the cargo type")
    description = fields.Text(
        string='Description',
        help="Provide a detailed description of the cargo type, such as characteristics, handling instructions, or any specific notes."
    )

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Cargo Type Code must be unique!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code'):
                vals['code'] = vals['code'].upper()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        return super().write(vals)

    def name_get(self):
        """
        Customize the display name of cargo types.
        Format: [CODE] Description
        """
        result = []
        for record in self:
            name = f'[{record.code}] {record.description or ""}'
            result.append((record.id, name))
        return result
