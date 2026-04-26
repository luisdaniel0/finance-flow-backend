from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

Base = declarative_base()
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
