from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from database import engine, SessionLocal, Base
from models import Transaction as TransactionModel
from models import Budget as BudgetModel


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Transaction(BaseModel):  # pydantic
    amount: float
    category: str
    date: str
    type: str


class Budget(BaseModel):  # pydantic
    name: str
    amount: float
    category: str


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/transactions/")
async def get_transactions(db=Depends(get_db)):

    transactions = db.query(TransactionModel).all()
    return transactions


@app.post("/transactions/")
async def create_transaction(transaction: Transaction, db=Depends(get_db)):
    new_transaction = TransactionModel(
        amount=transaction.amount,
        category=transaction.category,
        type=transaction.type,
        date=transaction.date,
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


@app.get("/transactions/{transaction_id}")
async def get_single_transaction(transaction_id: int, db=Depends(get_db)):
    transaction = (
        db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
    )
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction Not Found")
    return transaction


@app.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int, db=Depends(get_db)):
    transaction = (
        db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
    )
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction Not Found")
    db.delete(transaction)
    db.commit()
    return transaction


@app.get("/budgets/")
async def get_budgets(db=Depends(get_db)):
    budgets = db.query(BudgetModel).all()
    return budgets


@app.post("/budgets/")
async def create_budgets(budget: Budget, db=Depends(get_db)):
    new_budget = BudgetModel(
        name=budget.name, amount=budget.amount, category=budget.category
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return new_budget


@app.get("/budgets/{budget_id}")
async def get_single_budget(budget_id: int, db=Depends(get_db)):
    budget = db.query(BudgetModel).filter(BudgetModel.id == budget_id).first()

    return budget


@app.delete("/budgets/{budget_id}")
async def delete_budget(budget_id: int, db=Depends(get_db)):
    budget = db.query(BudgetModel).filter(BudgetModel.id == budget_id).first()
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget Not Found")

    db.delete(budget)
    db.commit()
    return budget
