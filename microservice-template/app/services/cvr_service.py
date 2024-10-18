import requests
from app.config import Settings
from dotenv import load_dotenv
import os


# Load environment variables from the .env file
load_dotenv()

# Now instantiate settings
settings = Settings()

class CVRService:
    def __init__(self):
        self.base_url = settings.CVR_API_URL
        self.auth = (settings.CVR_API_USERNAME, settings.CVR_API_PASSWORD)

    def get_cvr_id_by_company_name(self, company_name: str) -> int:
        """
        Searches for a company by name and returns its CVR-ID.
        """
        # Define the query for searching by company name
        query = {
            "query": {
                "match": {
                    "Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn": company_name
                }
            }
        }

        # Make the POST request to the ElasticSearch _search endpoint
        response = requests.post(
            f"{self.base_url}",
            auth=self.auth,
            json=query
        )

        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"ElasticSearch query failed with status code {response.status_code}")

        data = response.json()
        
        #print("cvr number of company:",data['hits']['hits'][0]['_source']['Vrvirksomhed']['cvrNummer'])
        
        # Safely access the CVR number
        try:
            cvr_id = data['hits']['hits'][0]['_source']['Vrvirksomhed']['cvrNummer']
            #cvr_id = data['hits']
            print("cvr number of company:", cvr_id)
            return cvr_id
        except KeyError as e:
            raise Exception(f"Key error accessing the CVR data: {str(e)}")
        except Exception as e:
            raise Exception(f"An error occurred while parsing the CVR response: {str(e)}")
