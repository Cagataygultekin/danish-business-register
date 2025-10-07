from fastapi import FastAPI
#from app.controller import api_router
from app.controller import cvr_controller

"""
def create_app():
    app = FastAPI()

    # Include the API router which has the references to all the endpoints
    app.include_router(api_router)

    return app
"""

def create_app():
    app = FastAPI(
        title="CVR Data API",
        description="API to retrieve CVR based data like General Information, Possible Ownership Information, Key Individuals, and Ownership Information.",
        version="1.0.0"
    )
    app.include_router(cvr_controller.router, prefix="/cvr", tags=["CVR"])
    return app