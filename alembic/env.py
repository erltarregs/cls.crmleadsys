# alembic/env.py

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# -- Make sure app/ is importable ---------------------------
# Adds the project root to Python's path so "from app.X import Y" works
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# -- Load .env before importing app modules --------------
load_dotenv()

# -- Import app components --------------------------------
from app.db.base import Base
from app.core.config import settings

# Import ALL models so Alembic sees them (via models/__init__.py)
import app.models # noqa: F401

# -- Alembic Config --------------------------------------
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Setup logging from alembic.ini
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is what Alembic inspectsto detect model changes
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
target_metadata = Base.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode / run migrations without a live DB connection.
    Generates a .sql file instead of executing directly.
    Useful for reviewing SQL before applying to production.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True, # detects column type changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    Run migrations against a live DB connection.
    This is what you use 99% of the time.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
