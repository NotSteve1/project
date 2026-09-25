import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from dotenv import load_dotenv

from alembic import context


# =====================================================
# PROJECT PATH SETUP
# =====================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


# =====================================================
# LOAD ENV
# =====================================================
load_dotenv(os.path.join(BASE_DIR, ".env"))


from app.database.db import Base
from app.models import User, Movie, Rating
 


# =====================================================
# ALEMBIC CONFIG
# =====================================================
config = context.config

database_url = os.getenv("DATABASE_URL")

if database_url:
    config.set_main_option("sqlalchemy.url", database_url)



if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except KeyError:
        pass


target_metadata = Base.metadata


# =====================================================
# OFFLINE MIGRATION
# =====================================================
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# =====================================================
# ONLINE MIGRATION
# =====================================================
def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()