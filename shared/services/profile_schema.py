from sqlalchemy import text


def ensure_profile_columns(db):
    """Add the profile name column to existing databases if it is missing."""
    statements = [
        ("teachers", "ALTER TABLE teachers ADD COLUMN name VARCHAR(100) NULL"),
        ("Admin", "ALTER TABLE Admin ADD COLUMN name VARCHAR(100) NULL"),
    ]

    for table_name, alter_sql in statements:
        exists = db.session.execute(
            text(
                """
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND table_name = :table_name
                  AND column_name = 'name'
                """
            ),
            {"table_name": table_name},
        ).scalar()

        if not exists:
            db.session.execute(text(alter_sql))

    db.session.commit()
