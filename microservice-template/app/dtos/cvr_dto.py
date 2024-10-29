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



#Ownership
class OwnershipInfo(BaseModel):
    owner_name: str
    ownership_percentage: str
    voting_percentage: str

class OwnershipResponse(BaseModel):
    cvr_number: int
    company_name: str
    legal_owners: List[str]
    beneficial_owners: List[str]
#######

#Key individuals
class KeyIndividual(BaseModel):
    name: str
    address: str

class KeyIndividualsResponse(BaseModel):
    management: List[KeyIndividual]
    board_of_directors: List[KeyIndividual]
    founders: List[KeyIndividual]
    fully_liable_partners: List[KeyIndividual]
####    


#Doesn't work part starts here
    ###
    ###
    ###
    
#Person
class PersonRequest(BaseModel):
    name: str

class PersonAffiliation(BaseModel):
    company_name: str
    role: str

class PersonInfoResponse(BaseModel):
    full_name: str
    address: str
    postal_code: str
    city: str
    affiliations: List[PersonAffiliation]
#####



    
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
    
