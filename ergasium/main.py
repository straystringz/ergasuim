import os
from dotenv import load_dotenv
from typing import List
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from passlib.context import CryptContext
from models import User, Task
from db import users_db
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pydantic import EmailStr
from email_validator import validate_email, EmailNotValidError


SECRET_KEY = "7fa69522aa02769082fa27770582e51a2e030b4bc7954f47ccd1ec0ef54ed538"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # noqa
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["password"]):  # noqa
        raise HTTPException(status_code=400, detail="Incorrect username or password")  # noqa
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/")
def root():
    return {"message": "Welcome to Ergasium"}


@app.post("/register")
def register(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")  # noqa
    hashed_password = hash_password(user.password)
    users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
    }
    return {"message": "User registered successfully"}


tasks_db = []

# Endpoints


@app.post("/tasks/", response_model=Task)
def create_task(task: Task, current_user: dict = Depends(get_current_user)):
    task.id = len(tasks_db) + 1
    Task.user = current_user["username"]
    tasks_db.append(task)
    return task


@app.get("/tasks/", response_model=List[Task])
def read_tasks(
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
):
    return [task for task in tasks_db if task.user == current_user["username"]][
        skip : skip + limit
    ]


@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, current_user: dict = Depends(get_current_user)):
    task = next(
        (
            task
            for task in tasks_db
            if task.id == task_id and task.user == current_user["username"]
        ),
        None,
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    updated_task: Task,
    current_user: dict = Depends(get_current_user),
):
    task = next(
        (
            task
            for task in tasks_db
            if task.id == task_id and task.user == current_user["username"]
        ),
        None,
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = updated_task.title
    task.description = updated_task.description
    task.due_date = updated_task.due_date
    task.priority = updated_task.priority
    task.completed = updated_task.completed
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: dict = Depends(get_current_user)):
    task = next(
        (
            task
            for task in tasks_db
            if task.id == task_id and task.user == current_user["username"]
        ),
        None,
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks_db.remove(task)
    return {"message": "Task deleted successfully"}


def send_email(subject: str, recipient: EmailStr, body: str):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USERNAME
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)


@app.post("/send-reminder/")
async def send_reminder(
    email: EmailStr, task_id: int, background_tasks: BackgroundTasks
):
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))

    task = next((task for task in tasks_db if task.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.due_date:
        subject = "Task Reminder: " + task.title
        body = f"Reminder: Your task '{task.title}' is due on {task.due_date}."
        background_tasks.add_task(send_email, subject, email, body)
        return {"message": "Reminder email sent successfully"}

    raise HTTPException(status_code=400, detail="Task does not have a due date")  # noqa
