from contextlib import contextmanager
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.types import JSON
from sqlalchemy import Table, Column, Integer, DateTime, Unicode, Boolean
from sqlalchemy.dialects.postgresql import insert as upsert_func

from opensanctions import settings

KEY_LEN = 255
VALUE_LEN = 65535
Conn = Connection

__all__ = ["Conn", "with_conn", "create_db", "upsert_func"]

assert (
    settings.DATABASE_URI is not None
), "Need to configure $OPENSANCTIONS_DATABASE_URI."

if not settings.DATABASE_URI.startswith("postgres"):
    raise RuntimeError("Unsupported database engine: %s" % settings.DATABASE_URI)

engine = create_engine(
    settings.DATABASE_URI,
    pool_size=settings.DATABASE_POOL_SIZE,
)


def create_db():
    metadata.create_all(bind=engine)


@contextmanager
def with_conn():
    with engine.begin() as conn:
        yield conn


metadata = MetaData()

issue_table = Table(
    "issue",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime, nullable=False),
    Column("level", Unicode(KEY_LEN), nullable=False),
    Column("module", Unicode(KEY_LEN)),
    Column("dataset", Unicode(KEY_LEN), index=True, nullable=False),
    Column("message", Unicode(VALUE_LEN)),
    Column("entity_id", Unicode(KEY_LEN), index=True),
    Column("entity_schema", Unicode(KEY_LEN)),
    Column("data", JSON, nullable=False),
)

resource_table = Table(
    "resource",
    metadata,
    Column("path", Unicode(KEY_LEN), primary_key=True, nullable=False),
    Column("dataset", Unicode(KEY_LEN), primary_key=True, index=True, nullable=False),
    Column("checksum", Unicode(KEY_LEN), nullable=False),
    Column("timestamp", DateTime, nullable=False),
    Column("mime_type", Unicode(KEY_LEN), nullable=True),
    Column("size", Integer, nullable=True),
    Column("title", Unicode(VALUE_LEN), nullable=True),
)

stmt_table = Table(
    "statement",
    metadata,
    Column("id", Unicode(KEY_LEN), primary_key=True, unique=True),
    Column("entity_id", Unicode(KEY_LEN), index=True, nullable=False),
    Column("canonical_id", Unicode(KEY_LEN), index=True, nullable=True),
    Column("prop", Unicode(KEY_LEN), nullable=False),
    Column("prop_type", Unicode(KEY_LEN), nullable=False),
    Column("schema", Unicode(KEY_LEN), nullable=False),
    Column("value", Unicode(VALUE_LEN), nullable=False),
    Column("dataset", Unicode(KEY_LEN), index=True),
    Column("target", Boolean, default=False, nullable=False),
    Column("unique", Boolean, default=False, nullable=False),
    Column("first_seen", DateTime, nullable=False),
    Column("last_seen", DateTime, index=True),
)

cache_table = Table(
    "cache",
    metadata,
    Column("url", Unicode(), index=True, nullable=False, unique=True),
    Column("text", Unicode(), nullable=True),
    Column("dataset", Unicode(), nullable=False),
    Column("timestamp", DateTime, index=True),
)

canonical_table = Table(
    "canonical",
    metadata,
    Column("entity_id", Unicode(KEY_LEN), index=True, nullable=False),
    Column("canonical_id", Unicode(KEY_LEN), index=False, nullable=True),
)