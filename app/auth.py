from fastapi import HTTPException
from .config import SECRET_KEY, ALGORITHM
from .db import users_db
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class InvalidCredentialsError(Exception):
    pass


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):  # noqa
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except JWTError as e:  # noqa
        raise HTTPException(status_code=500, detail="Token creation failed")
    return encoded_jwt


def login_user(username: str, password: str):
    if not username or not password:
        raise ValueError("Username and password are required")

    user = next((user for user in users_db if user["username"] == username), None)  # noqa
    if user is None or not verify_password(password, user["password"]):
        raise InvalidCredentialsError("Invalid credentials")

    return {
        "access_token": create_access_token({"sub": username}),
        "token_type": "bearer",
    }


def register_user(username: str, email: str, password: str):
    hashed_password = get_password_hash(password)
    user = {"username": username, "email": email, "password": hashed_password}
    users_db.append(user)
    return {"message": "User successfully registered"}
