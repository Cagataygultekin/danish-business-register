# Danish Business Register Microservice 

A FastAPI-based microservice for retrieving and processing company data from the [Danish Business Register (CVR)](https://datacvr.virk.dk). This project was developed at the Technical University of Munich as part of an interdisciplinary development project. It demonstrates scalable API design, data transformation, and automation for business and research use cases. 

## Features
- REST API endpoints built with **FastAPI** - Retrieve company details, ownership structures, and key individuals via the CVR API - Search companies by name or CVR ID - Download official company PDFs (via headless Selenium browser automation) - Structured JSON responses using **Pydantic DTOs** - Robust error handling and API rate-limit management - Environment-based configuration (no secrets in code) - Interactive API docs available via Swagger and ReDoc 

## 📂 Project Structure
app/ 
controller/ # FastAPI routers (API endpoints) 
services/ # Business logic and CVR API interactions 
dtos/ # Data Transfer Objects (request/response models) 
config.py # Environment configuration 
run.py # Entry point for FastAPI 
requirements.txt 

## Getting Started 

### Prerequisites 
- Python 3.8+
- Google Chrome installed (for PDF download functionality)

### Installation 
1. Clone the repository:
   bash
   git clone https://github.com/your-username/danish-business-register.git
   cd danish-business-register

2. Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows

3. Install dependencies:
   pip install -r requirements.txt

4. Set up your .env file in the project root:
   CVR_API_URL=...
   CVR_API_USERNAME=...
   CVR_API_PASSWORD=...
   ELASTICSEARCH_VERSION=6.8.16

5. Running the API:
   uvicorn run:app --reload

## API Endpoints

| Functionality                          | Endpoint                                       | Method |
|----------------------------------------|------------------------------------------------|--------|
| Get CVR ID by name                     | `/cvr/get-cvr-id`                              | POST   |
| Search companies by partial name        | `/cvr/get-companies-by-partial-name`           | POST   |
| Retrieve general company information    | `/cvr/get-general-info/{cvr_id}`               | GET    |
| Retrieve ownership details              | `/cvr/ownership/{cvr_id}`                      | GET    |
| Retrieve possible ownership information | `/cvr/get-possible-ownership-info/{cvr_id}`    | GET    |
| Retrieve key individuals                | `/cvr/get-key-individuals/{cvr_id}`            | GET    |
| Download company PDF                    | `/cvr/download-pdf`                            | POST   |
| Retrieve person information (restricted)| `/cvr/get-person-info`                         | GET    |


## Performance

Sub-second average response times, even for complex data structures

Handles large datasets and diverse company profiles

PDF downloads automated with headless Selenium Chrome

## Notes on Usage

Access to some CVR data requires authentication credentials provided by the Danish Business Authority.

This service is intended for educational, research, and demonstrational purposes.

Ensure compliance with CVR API terms.

## Use Cases

Researchers: Analyze company networks, ownership structures, and economic trends

Lawyers: Perform due diligence and verify company ownership structures

Businesses: Conduct competitor analysis, partnership evaluations, and risk assessments

Regulators: Support compliance monitoring (AML/KYC) and transparency requirements

## Tech Stack

FastAPI (web framework)

Uvicorn (ASGI server)

Selenium (PDF download automation)

ElasticSearch queries via CVR API

Python 3.8+
