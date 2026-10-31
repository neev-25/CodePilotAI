# from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker
# from dotenv import load_dotenv
# import os

# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

# print("DATABASE_URL =", DATABASE_URL)
# print("Current Working Directory =", os.getcwd())

# engine = create_engine(
#     DATABASE_URL,
#     connect_args={"check_same_thread": False},
# )

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine,
# )

# Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# SQLite requires check_same_thread=False; PostgreSQL does not support it.
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
_pool_options = (
    {}
    if DATABASE_URL.startswith("sqlite")
    else {"pool_pre_ping": True, "pool_recycle": 300, "pool_timeout": 30}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    **_pool_options,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
