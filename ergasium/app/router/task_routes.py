from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_all_tasks, create_task, update_task, delete_task, get_db

task_routes = APIRouter()


@task_routes.get("/tasks")
def read_tasks(db: Session = Depends(get_db)):
    tasks = get_all_tasks(db)
    return tasks


@task_routes.post("/tasks")
def add_task(task_data: dict, db: Session = Depends(get_db)):
    new_task = create_task(db, task_data)
    return new_task


@task_routes.put("/tasks/{task_id}")
def modify_task(task_id: int, task_data: dict, db: Session = Depends(get_db)):
    try:
        updated_task = update_task(db, task_id, task_data)
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@task_routes.delete("/tasks/{task_id}")
def remove_task(task_id: int, db: Session = Depends(get_db)):
    try:
        return delete_task(db, task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
