def migrate(env, version):
    env.execute("""
        ALTER TABLE account_move_line ADD COLUMN due_duration integer DEFAULT NULL;

        UPDATE account_move_line SET due_duration = (date_maturity - date)
    """)
