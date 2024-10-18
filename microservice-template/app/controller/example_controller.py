from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.dtos.example import ExampleRequest, Example
from app.services.example_service import ExampleService
from app.exceptions import ExampleException

router = APIRouter()
example_service = ExampleService()


class HTTPError(BaseModel):
    detail: str


@router.post(
    "/example",
    status_code=201,
    responses={
        201: {"description": "Example created successfully"},
        400: {"description": "Bad Request", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}})
def create_mandate(example_request: ExampleRequest):
    try:
        example_service.create_example(example_request)
        return {"message": "Mandate created successfully"}
    except ExampleException:
        raise HTTPException(status_code=404, detail="Excample Exception")
    except Exception as e:
        # TODO: Add logging to Sentry
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get(
    "/example/{example_id}",
    response_model=Example,
    responses={
        200: {"description": "Example"},
        404: {"description": "No Example found", "model": HTTPError},
        500: {"description": "Internal Server Error", "model": HTTPError}})
def get_mandates(example_id: int):
    try:
        example: Example = example_service.get_example(example_id)
        return example
    except ExampleException:
        raise HTTPException(status_code=404, detail="Example Exception")
    except Exception as e:
        # TODO: Add logging to Sentry
        raise HTTPException(status_code=500, detail="Internal Server Error")
