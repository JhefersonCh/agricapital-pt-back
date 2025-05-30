# ruff: noqa: F401
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from dotenv import load_dotenv
import sqlmodel
from sqlmodel import SQLModel
from app.shared.entities.requestEntity import Request
from app.shared.entities.credit_type_enity import CreditType
from app.shared.entities.request_status_entity import RequestStatus
from app.shared.entities.client_profile_entity import ClientProfile
from app.shared.entities.notifications_user_entity import NotificationsUser
from app.shared.entities.notification_entity import Notification

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))


def render_item(type_, obj, autogen_context):
    """
    Render a Python object for the migration script.
    This is used to ensure SQLModel types are correctly imported.
    """
    if type_ == "type" and isinstance(obj, sqlmodel.sql.sqltypes.AutoString):
        autogen_context.imports.add("import sqlmodel")
        return f"sqlmodel.sql.sqltypes.AutoString(length={obj.length})"
    return False


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        compare_type=True,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            compare_type=True,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
