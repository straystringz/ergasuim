from pydantic import BaseModel
from typing import List, Optional  # Noqa


class Task(BaseModel):
    # id: int
    title: str
    description: Optional[str] = None
    due_date: str
    priority: int
    completed: bool


class User(BaseModel):
    username: str
    email: str
    password: str


class TaskInResponse(Task):
    id: int


class UserInResponse(User):
    id: int


class TaskCreate(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    due_date: str
    priority: int
    completed: bool


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
