from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# PostgreSQL database URL using environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "5446")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "retail_analytics")

# Create a connection to the PostgreSQL server (without specifying the database)
try:
    engine = create_engine(
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/postgres",
        isolation_level="AUTOCOMMIT"
    )

    # Check if the database exists, and create it if it doesn't
    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{POSTGRES_DB}'"))
        if not result.scalar():
            connection.execute(text(f"CREATE DATABASE {POSTGRES_DB}"))
            print(f"Database '{POSTGRES_DB}' created successfully.")
        else:
            print(f"Database '{POSTGRES_DB}' already exists.")

    # Create a connection to the newly created or existing database
    SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

except SQLAlchemyError as e:
    print(f"Error connecting to the database: {e}")
    raise

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
