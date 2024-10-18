from app.dtos.example import ExampleRequest, Example
from typing import Optional


class ExampleService:
    @staticmethod
    def create_example(example_request: ExampleRequest):
        # example to create an example object
        pass

    @staticmethod
    def get_example(example_id: int) -> Optional[Example]:
        # Placeholder for retrieving an example object
        return None
