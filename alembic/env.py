# alembic/env.py

from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
from models import Base  # Adjust import path as needed
from main import SQLALCHEMY_DATABASE_URL

# This is the Alembic Config object, which provides access to the database settings
config = context.config

# Set up database URL from the config file
db_url = SQLALCHEMY_DATABASE_URL

# Create a SQLAlchemy engine
engine = engine_from_config(
    config.get_section(config.config_ini_section),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
)

# Apply database settings to the context
connection = engine.connect()
context.configure(
    connection=connection,
    target_metadata=Base.metadata  # Use your project's metadata object
)

# Make sure Alembic configures the logging properly
fileConfig(config.config_file_name)

# Inject your project's MetaData object into the Alembic context
with context.begin_transaction():
    context.run_migrations()
