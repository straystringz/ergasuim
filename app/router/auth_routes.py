from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import register_user, login_user, InvalidCredentialsError
from app.db import get_db
from sqlalchemy.orm import Session
from ..models import UserCreate

auth_routes = APIRouter()


@auth_routes.get("/auth")
def auth():
    return {"message": "Authentication routes"}


@auth_routes.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return register_user(user.username, user.email, user.password)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))  # noqa


@auth_routes.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = login_user(form_data.username, form_data.password)
        return {"access_token": user["access_token"], "token_type": "bearer"}
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
