from . import controllers
from . import models


def _set_default_value_for_column_existing(cr):
    cr.execute("""ALTER TABLE account_report_line ALTER COLUMN duration_term SET DEFAULT 'none'""")
    cr.execute("""ALTER TABLE account_report_line ALTER COLUMN duration_term_date_field SET DEFAULT 'date_maturity'""")


def post_init_hook(cr, registry):
    _set_default_value_for_column_existing(cr)
