from odoo import models, fields, api


class DgClass(models.Model):
    _name = 'freight.dg.class'
    _description = 'Dangerous Goods Class'

    code = fields.Char(string='Class Code', required=True, help="DG Class Code (e.g., Class 1, Class 2.1, etc.)")
    name = fields.Char(string='Class Name', required=True, help="Name of the Dangerous Goods Class", translate=True)
    description = fields.Text(string='Description', help="Detailed description of the hazardous material category")

    special_handling = fields.Text(
        string='Special Handling Instructions', translate=True,
        help="Special handling requirements for this DG class")
    un_number_ids = fields.One2many(
        'freight.un.number', 'dg_class_id', string='UN Numbers',
        help="List of UN Numbers (United Nations Numbers) representing specific substances categorized under this Dangerous Goods Class. "
            "These numbers are used for shipping declarations, labeling, and regulatory compliance.")
    un_number_count = fields.Integer(string='UN Number Count', compute='_compute_un_number_count')

    active = fields.Boolean(string='Active', default=True)

    def _compute_display_name(self):
        super()._compute_display_name()
        for dg_class in self:
            dg_class.display_name = f"{dg_class.code} - {dg_class.name}"

    @api.depends('un_number_ids')
    def _compute_un_number_count(self):
        read_group = self.env['freight.un.number']._read_group([('dg_class_id', 'in', self.ids)], ['dg_class_id'], ['dg_class_id'])
        mapped_count = {group['dg_class_id'][0]: group['dg_class_id_count'] for group in read_group}
        for dg_class in self:
            dg_class.un_number_count = mapped_count.get(dg_class.id, 0)

    def action_view_un_numbers(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('viin_freight_management.un_number_action')
        action['domain'] = [('dg_class_id', '=', self.id)]
        action['context'] = {
            'default_dg_class_id': self.id,
        }
        return action
