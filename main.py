from fastapi import FastAPI
from pydantic import BaseModel

class Transaction(BaseModel):
    amount: float
    category: str
    date: str
    type: str

app = FastAPI()

transactions_db = []

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/transactions/")
async def get_transactions():
    return transactions_db

@app.post("/transactions/")
async def create_transaction(transaction: Transaction):
    transactions_db.append(transaction)
    return transaction