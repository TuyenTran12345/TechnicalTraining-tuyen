from . import controllers
from . import models


def _set_default_value_for_column_existing(env):
    env.cr.execute("""ALTER TABLE account_report_line ALTER COLUMN duration_term SET DEFAULT 'none'""")
    env.cr.execute("""ALTER TABLE account_report_line ALTER COLUMN duration_term_date_field SET DEFAULT 'date_maturity'""")


def post_init_hook(env):
    _set_default_value_for_column_existing(env)
