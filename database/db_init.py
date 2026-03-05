from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
import sqlite3
from config import DATABASE_URL

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Enable SQLite foreign key support
@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

# Session & Base
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def init_db():
    from database import models
    from database.models import User
    from auth.security import hash_password

    Base.metadata.create_all(bind=engine)

    # Seed master account
    db = SessionLocal()
    existing = db.query(User).filter(User.username == "joel").first()
    if not existing:
        db.add(User(
            username="joel",
            email="your@email.com",
            hashed_password=hash_password("YourPassword123"),
            role="master",
            is_active=True
        ))
        db.commit()
    db.close()