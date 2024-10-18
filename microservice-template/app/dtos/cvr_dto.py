from pydantic import BaseModel

class CompanyRequest(BaseModel):
    name: str

class CompanyResponse(BaseModel):
    cvr_id: int
