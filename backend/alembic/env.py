from logging.config import fileConfig

import sqlalchemy as sa
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# `prepend_sys_path = .` in alembic.ini puts backend/ on sys.path when alembic
# is run from there, but Base and the models need to be importable regardless
# of invocation cwd, so make sure explicitly.
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings  # noqa: E402
from database import Base  # noqa: E402
# Import every model module so its table gets registered on Base.metadata --
# nothing else in the app imports models.game, since models/__init__.py only
# re-exports User/Group/GroupMember.
import models  # noqa: E402,F401
import models.game  # noqa: E402,F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Build the DB URL from the same settings/.env the app uses, so there's one
# source of truth instead of a second hardcoded URL in alembic.ini.
config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def include_object(object, name, type_, reflected, compare_to):
    # With include_schemas=True, autogenerate reflects everything in
    # DATABASE_SCHEMA, including the alembic_version table itself (it isn't
    # part of target_metadata) -- without this it shows up as a phantom
    # "removed table" on every autogenerate diff.
    if type_ == "table" and name == "alembic_version":
        return False
    return True

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=settings.DATABASE_SCHEMA,
        include_schemas=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # No search_path connect_args here (unlike database.py's app engine):
    # target_metadata already has every table schema-qualified (Base =
    # declarative_base(metadata=MetaData(schema=settings.DATABASE_SCHEMA))),
    # so emitted DDL is schema-qualified regardless. Setting search_path on
    # top of that made reflected FKs come back with referent_schema=None
    # (search-path-relative) while metadata's FKs are explicitly schema-
    # qualified, so autogenerate compared them as "different" and wanted to
    # drop+recreate every FK as a no-op on each run.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # The app's schema (e.g. bd_log) isn't `public`, so it must exist
        # before anything -- including the alembic_version table -- can be
        # created inside it, both on a fresh DB and in test schemas.
        connection.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS "{settings.DATABASE_SCHEMA}"'))
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=settings.DATABASE_SCHEMA,
            include_schemas=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
