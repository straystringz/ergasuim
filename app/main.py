from fastapi import FastAPI
from .router import auth_routes, task_routes, user_routes


app = FastAPI()

app.include_router(auth_routes)
app.include_router(task_routes)
app.include_router(user_routes)
