from .db import get_all_tasks, create_task
from .models import Task


def get_tasks():
    return get_all_tasks()


def create_new_task(task: Task):
    create_task(task)
