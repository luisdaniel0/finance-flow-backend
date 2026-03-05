from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


Base = declarative_base()
engine = create_engine(
    "postgresql://financeflowuser:password@localhost/financeflow", echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
