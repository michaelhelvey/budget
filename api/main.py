from copy import deepcopy
from typing import Optional
from datetime import datetime

from fastapi import Depends, FastAPI, Request, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api.auth import JWT_EXP, AuthProvider

from api.db import get_db_instance, save_state_to_file
from api.domain import ApplicationState, Transaction, User, get_monthly_report

app = FastAPI()

origins = ["http://localhost:3000", "https://budget.michaelhelvey.dev"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# wrap database in dependency so that we only save changes if the request
# succeeded
async def database():
    db = get_db_instance()
    try:
        yield db
        save_state_to_file(db)
    except Exception as e:
        print(f"Not saving database because there was an exception: {e}")


async def get_current_user(request: Request, db=Depends(database)):
    token = request.cookies.get("auth_token")
    auth = AuthProvider(db)
    user = auth.validate_token(token)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user


class LoginBody(BaseModel):
    email: str
    password: str


@app.post("/accounts/login")
async def read_root(body: LoginBody, response: Response, db=Depends(database)):
    auth = AuthProvider(db)

    user = auth.check_password(body.email, body.password)
    if not user:
        response.status_code = status.HTTP_401_UNAUTHORIZED
    else:
        token = auth.create_jwt_for_user(user)
        response.set_cookie(
            "auth_token",
            token,
            expires=datetime.now() - JWT_EXP,
            httponly=True,
            secure=True,
        )


class AccountsMeResponse(BaseModel):
    user: User


@app.get("/accounts/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return AccountsMeResponse(user=current_user)


class TransactionIn(BaseModel):
    category: str
    amount: int
    title: Optional[str]
    notes: Optional[str]


@app.post("/transactions")
async def create_transaction(
    transaction_body: TransactionIn,
    response: Response,
    current_user=Depends(get_current_user),
    db: ApplicationState = Depends(database),
):
    transaction = Transaction(
        **{
            **transaction_body.dict(),
            "created_at": datetime.now(),
            "user": current_user.email,
        }
    )
    db.get_current_state().transactions.append(transaction)
    response.status_code = status.HTTP_201_CREATED
    return transaction


@app.get("/_internal/state")
async def dump_state(
    user: User = Depends(get_current_user), db: ApplicationState = Depends(database)
):
    # note that this dumps users's password hashes, so it's not really a
    # longterm solution
    return db


@app.get("/months/current")
async def get_monthly_summary(
    user: User = Depends(get_current_user), db: ApplicationState = Depends(database)
):
    summary = get_monthly_report(db, db.get_current_state(), datetime.now())
