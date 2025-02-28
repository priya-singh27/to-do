from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine =create_engine(
    DATABASE_URL, connect_args={"check_same_thread":False}
)

SessionLocal =sessionmaker(autocommit=False ,autoflush=False,bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
def create_table():
    Base.metadata.create_all(bind=engine)