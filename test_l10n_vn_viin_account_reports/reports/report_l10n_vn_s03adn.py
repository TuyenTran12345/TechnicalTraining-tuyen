from odoo import models, api


class ReportL10nVnS03adn(models.AbstractModel):
    _name = 'report.l10n_vn_viin_account_reports.report_s03adn'
    _inherit = 'report.l10n_vn.common'
    _description = 'Vietnam S03a-DN Report'

    @api.model
    def _get_lines(self, data):
        cr = self.env.cr
        self.env['account.move.line'].check_access_rights('read')
        self.env['account.move.line'].check_access_rule('read')
        MoveLine = self.env['account.move.line']
        tables, where_clause, where_params = MoveLine.with_context(data['form'].get('used_context', {}))._query_get()
        wheres = []
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
        move_lines = []
        sql_sort = 'l.date, l.move_id, l.credit'
        currency_id = self.env['res.company'].browse(data['form']['company_id'][0]).currency_id
        decimal_places = currency_id.decimal_places

        if self.env['res.partner']._fields['name'].translate:
            select_partner_name = f"COALESCE(p.name->>'{self.env.lang}', p.name->>'en_US')"
        else:
            select_partner_name = 'p.name'

        sql = (f'''SELECT l.id AS lid, l.account_id AS account_id, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, l.date,
            m.name AS move_name, m.date AS move_date, acc.code AS account_code, m.state,
            STRING_AGG(acc2.code, ', ') AS counterpart, {select_partner_name} AS partner, c.name AS symbol_amount_currency, cc.name AS symbol_company_currency, l.amount_currency
            FROM account_move_line l
            JOIN account_move m ON (l.move_id=m.id)
            JOIN account_account acc ON (l.account_id = acc.id)
            LEFT JOIN account_ctp_account_rel acar ON (l.id = acar.aml_id)
            LEFT JOIN account_account acc2 ON (acc2.id = acar.account_id)
            LEFT JOIN res_partner p ON (l.partner_id = p.id)
            LEFT JOIN res_currency c ON (l.currency_id = c.id)
            LEFT JOIN res_currency cc ON (l.company_currency_id = cc.id)
            WHERE {filters}
            GROUP BY l.id, l.account_id, l.date, l.ref, l.name, m.name, m.date, acc.code, m.state, p.name, c.name , cc.name ORDER BY {sql_sort}'''
        )
        params = (tuple(where_params))
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            row['decimal_places'] = decimal_places
            if row['amount_currency']:
                row['exchange_rate'] = abs((float(row['debit']) + float(row['credit'])) / float(row['amount_currency']))
            else:
                row['exchange_rate'] = 1
            move_lines.append(row)
        return move_lines
