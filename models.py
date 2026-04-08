from sqlalchemy import Column, Integer, Float, String, ForeignKey

from database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    date = Column(String)
    category = Column(String)
    type = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))


class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    amount = Column(Float)
    category = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    email = Column(String, unique=True)
