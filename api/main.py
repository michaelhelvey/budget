from datetime import datetime
import http
from typing import Union

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api.auth import JWT_EXP, AuthProvider

from api.db import get_db_instance, save_state_to_file
from api.domain import User

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


async def get_current_user(request: Request, db = Depends(database)):
    token = request.cookies.get("auth_token")
    auth = AuthProvider(db)
    return auth.validate_token(token)


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
async def read_item(response_model=AccountsMeResponse, current_user: User = Depends(get_current_user)):
    return AccountsMeResponse(user=current_user)
