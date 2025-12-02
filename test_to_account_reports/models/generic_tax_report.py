from odoo import api, models, _
from odoo.tools import groupby
from odoo.osv import expression


# pylint: disable=consider-merging-classes-inherited
class GenericTaxReport(models.Model):
    _inherit = 'account.report'

    def _get_customs_lines_generic_tax(self, filter_options, columns):
        return self._get_customs_lines_generic_tax_balance(filter_options, columns, ['tax_id'])

    def _get_customs_lines_generic_tax_report_account_tax(self, filter_options, columns):
        return self._get_customs_lines_generic_tax_balance(filter_options, columns, ['base_account_id', 'tax_id'])

    def _get_customs_lines_generic_tax_report_tax_account(self, filter_options, columns):
        return self._get_customs_lines_generic_tax_balance(filter_options, columns, ['tax_id', 'base_account_id'])

    def _get_customs_lines_generic_tax_balance(self, filter_options, columns, mode):

        def _calculate_grouped_values(datas, key, parent_line_id=False, level=1):
            return {
                'base_line_ids': [item['base_line_id'] for item in datas],
                'net': abs(sum(item['base_amount'] for item in datas)),
                'tax': abs(sum(item['tax_amount'] for item in datas)),
                'type_tax_use': datas[0]['type_tax_use'],
                'parent_id': parent_line_id,
                'level': level,
                'id': key
            }

        def _group_and_append(data, grouping_keys, parent_line_id, parent_level, columns):
            if not grouping_keys:
                return

            current_key = grouping_keys[0]
            remaining_keys = grouping_keys[1:]
            prepare_func = grouping_keys_funcs.get(current_key)

            for key, sub_group in groupby(data, lambda l: l[current_key]):
                values = _calculate_grouped_values(sub_group, key, parent_line_id, parent_level + 1)
                sub_line = prepare_func(values, columns=columns)
                sub_parent_id = sub_line['id']
                sub_level = sub_line['level'] + 1
                lines.append(sub_line)

                _group_and_append(sub_group, remaining_keys, sub_parent_id, sub_level, columns)

        base_domain = [
            '|',
            ('move_id.move_type', 'in', self.env['account.move'].get_sale_types(include_receipts=True)),
            ('move_id.move_type', 'in', self.env['account.move'].get_purchase_types(include_receipts=True))
        ]
        tax_details_res = self._get_customs_lines_data_generic_tax(
            filter_options, date_scope='strict_range', extend_domain=expression.AND([
                base_domain, [('tax_repartition_line_id', '!=', False)]
            ])
        )
        tax_exemption_details_res = self._get_customs_lines_data_exemption_tax(
            filter_options, date_scope='strict_range', extend_domain=expression.AND([
                base_domain, [('display_type', '=', 'product'), ('tax_ids', '!=', False), ('id', 'not in', [item['base_line_id'] for item in tax_details_res])]
            ])
        )
        tax_details_res.extend(tax_exemption_details_res)
        lines = []
        grouping_keys_funcs = self._get_customs_lines_generic_tax_report_grouping_key_func()

        for type_tax_use, line_vals in groupby(tax_details_res, lambda l: l['type_tax_use']):
            tax_use_line = self._prepare_customs_line_tax_report_vals(
                _calculate_grouped_values(line_vals, type_tax_use), columns=columns
            )
            tax_use_line_id = tax_use_line['id']
            parent_level = tax_use_line['level']
            lines.append(tax_use_line)

            _group_and_append(line_vals, mode, tax_use_line_id, parent_level, columns)
        return lines

    @api.model
    def _get_customs_lines_generic_tax_report_grouping_key_func(self):
        return {
            'tax_id': self._prepare_customs_line_detail_tax_vals,
            'base_account_id': self._prepare_customs_line_detail_account_vals
        }

    @api.model
    def _get_customs_lines_data_generic_tax(self, filter_options, date_scope='strict_range', extend_domain=None):
        table, where_clauses, where_params = self._get_sql(
            filter_options, date_scope=date_scope, extend_domain=extend_domain
        )
        tax_details_query, tax_details_params = self.env['account.move.line']._get_query_tax_details(
            table, where_clauses, where_params, fallback=True
        )
        self.env['account.move.line'].flush_model()
        self.env.cr.execute(f"""
            SELECT
                at.type_tax_use AS type_tax_use,
                tb_tax_detail.tax_id AS tax_id,
                tb_tax_detail.base_account_id AS base_account_id,
                tb_tax_detail.base_line_id AS base_line_id,
                tb_tax_detail.base_amount AS base_amount,
                tb_tax_detail.tax_amount AS tax_amount
            FROM ({tax_details_query}) AS tb_tax_detail
            LEFT JOIN account_tax AS at ON at.id = tb_tax_detail.tax_id
            ORDER BY at.type_tax_use, tb_tax_detail.tax_id, tb_tax_detail.base_account_id
        """, tax_details_params)
        tax_details_res = self.env.cr.dictfetchall()
        return tax_details_res

    def _get_customs_lines_data_exemption_tax(self, filter_options, date_scope='strict_range', extend_domain=None):
        table, where_clauses, where_params = self._get_sql(
            filter_options, date_scope=date_scope, extend_domain=extend_domain
        )
        self.env['account.move.line'].flush_model()
        query = f"""
            SELECT
                at.type_tax_use,
                rel.account_tax_id AS tax_id,
                aa.id AS base_account_id,
                account_move_line.id AS base_line_id,
                account_move_line.balance AS base_amount,
                0 AS tax_amount
            FROM {table}
            LEFT JOIN account_move_line_account_tax_rel as rel ON rel.account_move_line_id = account_move_line.id
            LEFT JOIN account_tax AS at ON at.id = rel.account_tax_id
            LEFT JOIN account_account AS aa ON aa.id = account_move_line.account_id
            WHERE {where_clauses}
        """
        self.env.cr.execute(query, where_params)
        tax_exemption_details_res = self.env.cr.dictfetchall()
        return tax_exemption_details_res

    @api.model
    def _get_supported_type_tax_use(self):
        return {
            'sale': _('Sales'),
            'purchase': _('Purchases'),
        }

    @api.model
    def _prepare_customs_line_tax_report_vals(self, result, columns, is_unaffected_earnings=False):
        supported_type_tax_use = self._get_supported_type_tax_use()
        res = {
            'id': f'~account.tax.use~{result["id"]}',
            'name': '%s' % supported_type_tax_use.get(result["type_tax_use"], _('None')),
            'display_code': '',
            'level': 1,
            'parent_id': '',
            'class': 'account_report_level1 fw-bolder',
            'unfoldable': False,
            'unfolded': False,
            'is_expanded_line': False,
            'is_customs_line': True,
            'visible': True,
            'groupby': 'id',
            'columns': self._build_custom_line_columns(result, columns),
            'is_unaffected_earnings': is_unaffected_earnings
        }
        action_domain = [('id', 'in', result['base_line_ids'])]
        action_dict = {
            'name': _("Journal Items"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_type': 'list',
            'view_mode': 'list',
            'views': [[False, 'list'], [False, 'form']],
            'domain': action_domain,
        }

        res['action_dict'] = action_dict
        return res

    @api.model
    def _prepare_customs_line_detail_tax_vals(self, result, columns, is_unaffected_earnings=False):
        tax = self.env['account.tax'].browse(result['id'])
        parent_id = result['parent_id']
        level = result['level']
        line_id = result["id"]
        res = {
            'id': f'{parent_id}~account.tax~{line_id}',
            'name': tax.display_name,
            'display_code': '',
            'level': level,
            'parent_id': result['parent_id'],
            'class': f'account_report_level{level}',
            'unfoldable': False,
            'unfolded': False,
            'is_expanded_line': False,
            'is_customs_line': True,
            'visible': True,
            'groupby': 'id',
            'columns': self._build_custom_line_columns(result, columns),
            'is_unaffected_earnings': is_unaffected_earnings
        }
        action_domain = [('id', '=', result['base_line_ids'])]
        action_dict = {
            'name': _("Journal Items"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_type': 'list',
            'view_mode': 'list',
            'views': [[False, 'list'], [False, 'form']],
            'domain': action_domain,
        }

        res['action_dict'] = action_dict
        return res

    @api.model
    def _prepare_customs_line_detail_account_vals(self, result, columns, is_unaffected_earnings=False):
        account = self.env['account.account'].browse(result['id'])
        parent_id = result['parent_id']
        level = result['level']
        line_id = result['id']
        res = {
            'id': f'{parent_id}~account.account~{line_id}',
            'name': account.display_name,
            'display_code': '',
            'level': level,
            'parent_id': result['parent_id'],
            'class': f'account_report_level{level}',
            'unfoldable': False,
            'unfolded': False,
            'is_expanded_line': False,
            'is_customs_line': True,
            'visible': True,
            'groupby': 'id',
            'columns': self._build_custom_line_columns(result, columns),
            'is_unaffected_earnings': is_unaffected_earnings
        }
        action_domain = [('id', '=', result['base_line_ids'])]
        action_dict = {
            'name': _("Journal Items"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_type': 'list',
            'view_mode': 'list',
            'views': [[False, 'list'], [False, 'form']],
            'domain': action_domain,
        }

        res['action_dict'] = action_dict
        return res
