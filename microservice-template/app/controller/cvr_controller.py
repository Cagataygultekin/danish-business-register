from fastapi import APIRouter, HTTPException
from app.services.cvr_service import CVRService
from app.dtos.cvr_dto import CompanyRequest, CompanyResponse

router = APIRouter()
cvr_service = CVRService()

@router.post("/get-cvr-id", response_model=CompanyResponse)
def get_cvr_id(company_request: CompanyRequest):
    """
    Endpoint to retrieve the CVR-ID of a company by its name.
    """
    try:
        print(f"Received request for company: {company_request.name}")
        cvr_id = cvr_service.get_cvr_id_by_company_name(company_request.name)
        print(f"Fetched CVR ID: {cvr_id}")
        return CompanyResponse(cvr_id=cvr_id)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

