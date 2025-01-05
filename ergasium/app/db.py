# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# In-memory user and task databases for simplicity
users_db = []
tasks_db = []


def get_all_tasks(db: Session):
    return tasks_db


def create_task(db: Session, task_data):
    if "id" not in task_data:
        task_data["id"] = len(tasks_db) + 1
    tasks_db.append(task_data)
    return task_data


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def update_task(db: Session, task_id: int, task_data: dict):
    for task in tasks_db:
        if task["id"] == task_id:
            task.update(task_data)
            return task
    raise ValueError("Task not found")


def delete_task(db: Session, task_id: int):
    global tasks_db
    tasks_db = [task for task in tasks_db if task["id"] != task_id]
    return {"message": "Task deleted"}
