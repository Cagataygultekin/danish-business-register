from pydantic import BaseModel
from typing import List, Optional

#Get one CVR id from company name
#Input
class CompanyRequest(BaseModel):
    name: str

#Output
class CompanyResponse(BaseModel):
    cvr_id: int
    
####

#Get many companies and cvr numbers by one partial company name
#Input
class CompanyInfo(BaseModel):
    company_name: str
    cvr_number: int

#Output
class CompanySearchResponse(BaseModel):
    total_results: int
    results: List[CompanyInfo]



class GeneralInfoResponse(BaseModel):
    company_name: str
    cvr_number: int
    address: str
    postal_code: str
    city: str
    start_date: str
    business_type: str
    advertising_protection: str
    status: str

    
####not working correctly
class CompanyDataResponse(BaseModel):
    cvr_id: int
    company_name: str
    company_type: Optional[str] = None
    registration_date: Optional[str] = None
    termination_date: Optional[str] = None  # Add termination date
    status: Optional[str] = None
    address: Optional[str] = None
    industry_code: Optional[str] = None
    contact_information: Optional[str] = None  # Add contact information
    number_of_employees: Optional[int] = None  # Add number of employees
    personnel_circle: Optional[str] = None  # Add personnel circle
    subscription_rule: Optional[str] = None  # Add subscription rule
    registered_capital: Optional[str] = None  # Add registered capital
    
