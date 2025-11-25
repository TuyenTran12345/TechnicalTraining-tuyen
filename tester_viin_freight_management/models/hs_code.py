from odoo import models, fields, api


class HSCode(models.Model):
    _name = 'hs.code'
    _description = 'HS Code'
    _rec_name = 'code'

    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description', translate=True)

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'HS Code must be unique!')
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

    def _compute_display_name(self):
        super()._compute_display_name()
        for record in self:
            record.display_name = f'[{record.code}] {record.description or ""}'
