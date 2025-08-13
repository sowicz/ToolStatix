from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://localhost:3306/toolstatix_database?user=appAdmin&password=appJaipur2025"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://appAdmin:appJaipur2025@localhost:3306/toolstatix_database?charset=utf8mb4"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()