from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import all models so Alembic can detect them ────────────────────────────
from app.database.database import Base
from app.core.config import settings

# Ensure every model module is imported (triggers SQLAlchemy table registration)
import app.models.user  # noqa: F401
import app.models.repository  # noqa: F401
import app.models.indexing_job  # noqa: F401
import app.models.analysis_cache  # noqa: F401
import app.models.task  # noqa: F401
import app.models.ai_usage_log  # noqa: F401

target_metadata = Base.metadata

# Override alembic.ini sqlalchemy.url with the app settings value
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
# ────────────────────────────────────────────────────────────────────────────


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
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
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
