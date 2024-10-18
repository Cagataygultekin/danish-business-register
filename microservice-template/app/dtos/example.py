from pydantic import BaseModel, Field


__all__ = ['ExampleRequest', 'Example']


class ExampleRequest(BaseModel):
    name: str
    country: str = Field(..., min_length=1)


class Example(BaseModel):
    company_id: str
