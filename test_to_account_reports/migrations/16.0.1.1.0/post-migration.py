from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """
    Migration to reset cash flow line configurations.
    Resets groupby, use_reconcile, reconcile_domain fields
    for specific cash flow line records.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Configuration for records and their fields to reset
    records_config = {
        'to_account_reports.cash_flow_line_02_04_01': ['groupby'],
        'to_account_reports.cash_flow_line_02_04_01_expr_01': [
            'use_reconcile', 'reconcile_domain'
        ],
        'to_account_reports.cash_flow_line_02_04_02': ['groupby'],
        'to_account_reports.cash_flow_line_02_04_02_expr_01': [
            'use_reconcile', 'reconcile_domain'
        ]
    }

    # Process each record configuration
    for record_id, fields_to_reset in records_config.items():
        record = env.ref(record_id, raise_if_not_found=False)
        if not record:
            continue

        # Reset each field if it has a truthy value
        for field_name in fields_to_reset:
            current_value = getattr(record, field_name, None)
            if current_value:
                setattr(record, field_name, False)
