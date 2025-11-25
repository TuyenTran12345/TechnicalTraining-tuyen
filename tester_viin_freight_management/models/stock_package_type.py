from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPackageType(models.Model):
    _inherit = 'stock.package.type'

    is_container = fields.Boolean(
        string='Is Container',
        help="If checked, the package type will be treated as a container."
    )
    volume = fields.Float(
        string='Volume',
        compute='_compute_volume', store=True, readonly=False,
        help="The volume used for logistics calculations. Can be calculated automatically "
            "from dimensions or entered manually for more accuracy."
    )

    @api.constrains('volume')
    def _check_volume(self):
        for record in self:
            if record.volume < 0:
                raise ValidationError(_("Volume of Package Type %s cannot be negative") % record.name)

    @api.depends('packaging_length', 'width', 'height')
    def _compute_volume(self):
        for record in self:
            volume = record.packaging_length * record.width * record.height
            record.volume = volume

    def _compute_length_uom_name(self):
        """
        By default, Odoo does not set the value for `length_uom_name` when editing package type
        (commit: https://github.com/odoo/odoo/pull/119805/commits/75f4533e723e4662436f119f5b00f8400b10cb0e).

        However, in Freight Management, users need to know the length unit (mm, cm, m)
        when creating **packages** or **cargo commodities**.

        - The default value of `length_uom_name` in Odoo is **mm**
        (commit: https://github.com/odoo/odoo/pull/64735/commits/9bbf26f303d04903056935551a33517fc29b51d1).
        - In the Freight Business, forwarders usually use **m³** instead of **mm**.

        Therefore, we need to **recompute `length_uom_name`** to display the unit when configuring the package type,
        helping the user understand that they are filling in **mm** information, not **m**.
        """
        super(StockPackageType, self)._compute_length_uom_name()
        for record in self:
            record.length_uom_name = self.env['product.template']._get_length_uom_name_from_ir_config_parameter()
