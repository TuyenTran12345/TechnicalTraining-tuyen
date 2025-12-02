from odoo import fields, models


# pylint: disable=consider-merging-classes-inherited
class ExecutiveSummaryReport(models.Model):
    _inherit = 'account.report'

    def _report_custom_executive_summary_ndays(self, filter_options, date_scope=None):
        date_to = fields.Date.from_string(filter_options['current_date']['date_to'])
        date_from = fields.Date.from_string(filter_options['current_date']['date_from'])
        return {'value': (date_to - date_from).days}
