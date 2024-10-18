from fastapi import APIRouter, HTTPException
from app.services.cvr_service import CVRService
from app.dtos.cvr_dto import CompanyRequest, CompanyResponse, CompanyInfo, CompanySearchResponse, CompanyDataResponse, GeneralInfoResponse

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
    
@router.post("/get-companies-by-partial-name", response_model=CompanySearchResponse)
def get_companies_by_partial_name(company_request: CompanyRequest):
    """
    Endpoint to retrieve full company names and CVR numbers by partial company name.
    """
    try:
        print(f"Received request for partial company name: {company_request.name}")
        results = cvr_service.get_companies_by_partial_name(company_request.name)
        if not results:
            raise HTTPException(status_code=404, detail="No companies found with the given partial name.")

        # Format the response
        companies_info = [CompanyInfo(company_name=company["company_name"], cvr_number=company["cvr_number"]) for company in results]
        return CompanySearchResponse(total_results=len(companies_info), results=companies_info)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    


@router.get("/get-general-info/{cvr_id}", response_model=GeneralInfoResponse)
def get_general_info(cvr_id: int):
    """
    Endpoint to retrieve general company information by CVR ID.
    """
    try:
        general_info = cvr_service.get_general_info_by_cvr_id(cvr_id)
        return GeneralInfoResponse(
            company_name=general_info["company_name"],
            cvr_number=general_info["cvr_number"],
            address=general_info["address"],
            postal_code=general_info["postal_code"],
            city=general_info["city"],
            start_date=general_info["start_date"],
            business_type=general_info["business_type"],
            advertising_protection=general_info["advertising_protection"],
            status=general_info["status"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))








#not working correctly
@router.get("/get-company-data/{cvr_id}", response_model=CompanyDataResponse)
def get_company_data(cvr_id: int):
    """
    Endpoint to retrieve detailed company data by CVR ID.
    """
    try:
        print(f"Received request for company data with CVR ID: {cvr_id}")
        company_data = cvr_service.get_company_data_by_cvr_id(cvr_id)

        # Map the company data to the response model
        response = CompanyDataResponse(
            cvr_id=company_data.get('cvr_id'),
            company_name=company_data.get('company_name'),
            company_type=company_data.get('company_type'),
            registration_date=company_data.get('registration_date'),
            termination_date=company_data.get('termination_date'),
            status=company_data.get('status'),
            address=company_data.get('address'),
            industry_code=company_data.get('industry_code'),
            contact_information=company_data.get('contact_information'),
            number_of_employees=company_data.get('number_of_employees'),
            personnel_circle=company_data.get('personnel_circle'),
            subscription_rule=company_data.get('subscription_rule'),
            registered_capital=company_data.get('registered_capital')
        )

        return response
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))







  

