from fastapi import APIRouter
from app.controller import example_controller

api_router = APIRouter()
api_router.include_router(example_controller.router, prefix="", tags=["Example"])
