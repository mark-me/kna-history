# content_db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Change this path to wherever you want the db file
SQLITE_URL = "sqlite:///kna_archive.db"  # relative to current dir
# Or absolute: "sqlite:////full/path/to/kna_archive.db"

engine = create_engine(SQLITE_URL, echo=False)  # echo=True for debugging

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,  # enables SQLAlchemy 2.0 style
)


def get_session():
    """Factory / dependency to get a new session.
    Use this in services, FastAPI dependencies, scripts, etc.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# If your models are in the same package, import them here or ensure
# they are imported before create_all()
def create_all_tables():

    Base.metadata.create_all(bind=engine)
    print("All tables created (or already exist).")


def create_database(db_path="data/kna_archive.db"):
    """
    Create or update the database schema (tables + indexes defined in models).
    Safe to call multiple times.
    """

    # Override engine if custom path is given (useful for testing)
    custom_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=custom_engine)

    print(f"Database created/updated with all tables and indexes at: {db_path}")
    return custom_engine


if __name__ == "__main__":
    create_all_tables()
    create_database()
