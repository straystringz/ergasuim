from fastapi import APIRouter

user_routes = APIRouter()


@user_routes.get("/users")
def get_users():
    return {"message": "List of users"}
