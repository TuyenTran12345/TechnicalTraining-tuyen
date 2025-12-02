def migrate(cr, version):
    cr.execute("""ALTER TABLE account_report_line ALTER COLUMN duration_term SET DEFAULT 'none'""")
    cr.execute("""ALTER TABLE account_report_line ALTER COLUMN duration_term_date_field SET DEFAULT 'date_maturity'""")
