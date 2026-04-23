from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from database import engine, SessionLocal, Base
from models import Transaction as TransactionModel
from models import Budget as BudgetModel
from models import User as UserModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

SECRET_KEY = "SUPERSECRETCODE123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"])


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_token(username):
    user_info = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    encoded_user = jwt.encode(user_info, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_user


async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Unauthorized")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user is None:
        raise credentials_exception

    return user


class Transaction(BaseModel):  # pydantic
    amount: float
    category: str
    date: str
    type: str


class Budget(BaseModel):  # pydantic
    name: str
    amount: float
    category: str


class User(BaseModel):
    username: str
    password: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/transactions/")
async def get_transactions(db=Depends(get_db), current_user=Depends(get_current_user)):

    transactions = (
        db.query(TransactionModel)
        .filter(TransactionModel.user_id == current_user.id)
        .order_by(TransactionModel.id)
        .all()
    )
    return transactions


@app.post("/transactions/")
async def create_transaction(
    transaction: Transaction, db=Depends(get_db), current_user=Depends(get_current_user)
):
    new_transaction = TransactionModel(
        amount=transaction.amount,
        category=transaction.category,
        type=transaction.type,
        date=transaction.date,
        user_id=current_user.id,
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


@app.get("/transactions/{transaction_id}")
async def get_single_transaction(
    transaction_id: int, db=Depends(get_db), current_user=Depends(get_current_user)
):
    transaction = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.id == transaction_id,
            TransactionModel.user_id == current_user.id,
        )
        .first()
    )
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction Not Found")
    return transaction


@app.put("/transactions/{transaction_id}")
async def edit_transaction(
    transaction: Transaction,
    transaction_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    edit_transaction = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.id == transaction_id,
            TransactionModel.user_id == current_user.id,
        )
        .first()
    )

    if edit_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction Not Found")

    edit_transaction.amount = transaction.amount
    edit_transaction.category = transaction.category
    edit_transaction.type = transaction.type
    edit_transaction.date = transaction.date

    db.commit()
    db.refresh(edit_transaction)
    return edit_transaction


@app.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: int, db=Depends(get_db), current_user=Depends(get_current_user)
):
    transaction = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.id == transaction_id,
            TransactionModel.user_id == current_user.id,
        )
        .first()
    )
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction Not Found")
    db.delete(transaction)
    db.commit()
    return transaction


@app.get("/budgets/")
async def get_budgets(db=Depends(get_db), current_user=Depends(get_current_user)):
    budgets = (
        db.query(BudgetModel)
        .filter(BudgetModel.user_id == current_user.id)
        .order_by(BudgetModel.id)
        .all()
    )
    return budgets


@app.post("/budgets/")
async def create_budgets(
    budget: Budget, db=Depends(get_db), current_user=Depends(get_current_user)
):
    new_budget = BudgetModel(
        name=budget.name,
        amount=budget.amount,
        category=budget.category,
        user_id=current_user.id,
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return new_budget


@app.get("/budgets/{budget_id}")
async def get_single_budget(
    budget_id: int, db=Depends(get_db), current_user=Depends(get_current_user)
):
    budget = (
        db.query(BudgetModel)
        .filter(BudgetModel.id == budget_id, BudgetModel.user_id == current_user.id)
        .first()
    )

    return budget


@app.delete("/budgets/{budget_id}")
async def delete_budget(
    budget_id: int, db=Depends(get_db), current_user=Depends(get_current_user)
):
    budget = (
        db.query(BudgetModel)
        .filter(BudgetModel.id == budget_id, BudgetModel.user_id == current_user.id)
        .first()
    )
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget Not Found")

    db.delete(budget)
    db.commit()
    return budget


@app.put("/budgets/{budget_id}")
async def update_budget(
    budget: Budget,
    budget_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    edit_budget = (
        db.query(BudgetModel)
        .filter(BudgetModel.id == budget_id, BudgetModel.user_id == current_user.id)
        .first()
    )
    if edit_budget is None:
        raise HTTPException(status_code=404, detail="Budget Not Found")

    edit_budget.name = budget.name
    edit_budget.amount = budget.amount
    edit_budget.category = budget.category
    db.commit()
    db.refresh(edit_budget)
    return edit_budget


@app.post("/users/sign-up")
async def create_user(user: User, db=Depends(get_db)):
    find_user = db.query(UserModel).filter(
        (UserModel.username == user.username) | (UserModel.email == user.email)
    ).first()

    if find_user is not None:
        raise HTTPException(status_code=409, detail="User already exists")

    new_user = UserModel(
        username=user.username,
        hashed_password=pwd_context.hash(user.password),
        email=user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/users/login")
async def user_login(user: User, db=Depends(get_db)):
    find_user = db.query(UserModel).filter(UserModel.username == user.username).first()

    if find_user is None:
        raise HTTPException(status_code=404, detail="User Not Found")

    if pwd_context.verify(user.password, find_user.hashed_password) is True:
        return create_token(user.username)
    else:
        raise HTTPException(status_code=401, detail="Incorrect password")
