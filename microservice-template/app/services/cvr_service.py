import requests
from app.config import Settings
from dotenv import load_dotenv
import os
import json

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
        query = {
            "query": {
                "match": {
                    "Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn": company_name
                }
            }
        }

        response = requests.post(
            f"{self.base_url}",
            auth=self.auth,
            json=query
        )

        if response.status_code != 200:
            raise Exception(f"ElasticSearch query failed with status code {response.status_code}")

        data = response.json()

        try:
            cvr_id = data['hits']['hits'][0]['_source']['Vrvirksomhed']['cvrNummer']
            print("CVR number of company:", cvr_id)
            return cvr_id
        except KeyError as e:
            raise Exception(f"Key error accessing the CVR data: {str(e)}")
        except Exception as e:
            raise Exception(f"An error occurred while parsing the CVR response: {str(e)}")

    def get_companies_by_partial_name(self, partial_name: str) -> list:
        """
        Searches for companies by partial name and returns a list of full company names and CVR numbers.
        """
        # Initial query to get the total number of hits
        query = {
            "size": 0,  # Set to 0 initially to only get the total count
            "query": {
                "match_phrase_prefix": {
                    "Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn": partial_name
                }
            }
        }

        response = requests.post(
            f"{self.base_url}",
            auth=self.auth,
            json=query
        )

        if response.status_code != 200:
            raise Exception(f"ElasticSearch query failed with status code {response.status_code}")

        data = response.json()

        # Get the total number of hits (matching companies)
        total = data['hits']['total']

        # Handle both possible cases: total as an int or total as a dict
        if isinstance(total, dict):
            total_hits = total['value']  # for newer versions where 'total' is a dict
        else:
            total_hits = total  # for older versions where 'total' is an int

        if total_hits == 0:
            return []  # No matches found

        # Now that we know the total hits, fetch all results
        query = {
            "size": total_hits,  # Dynamically fetch all results
            "query": {
                "match_phrase_prefix": {
                    "Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn": partial_name
                }
            }
        }

        response = requests.post(
            f"{self.base_url}",
            auth=self.auth,
            json=query
        )

        if response.status_code != 200:
            raise Exception(f"ElasticSearch query failed with status code {response.status_code}")

        data = response.json()

        results = []
        try:
            hits = data['hits']['hits']
            for hit in hits:
                company_name = hit['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteNavn']['navn']
                cvr_number = hit['_source']['Vrvirksomhed']['cvrNummer']
                results.append({
                    "company_name": company_name,
                    "cvr_number": cvr_number
                })
            return results
        except KeyError as e:
            raise Exception(f"Key error accessing the CVR data: {str(e)}")
        except Exception as e:
            raise Exception(f"An error occurred while parsing the CVR response: {str(e)}")
        
        
    

    def get_general_info_by_cvr_id(self, cvr_id: int) -> dict:
        """
        Searches for a company by CVR ID and returns its general information.
        """
        query = {
            "query": {
                "match": {
                    "Vrvirksomhed.cvrNummer": cvr_id
                }
            }
        }

        response = requests.post(
            f"{self.base_url}",
            auth=self.auth,
            json=query
        )

        if response.status_code != 200:
            raise Exception(f"ElasticSearch query failed with status code {response.status_code}")

        data = response.json()

        total_hits = data['hits']['total']
        if isinstance(total_hits, dict):
            total_hits = total_hits.get('value', 0)
        elif isinstance(total_hits, int):
            total_hits = total_hits
        else:
            raise Exception("Unexpected format for total hits")

        if total_hits == 0:
            raise Exception(f"No company found with CVR ID: {cvr_id}")

        try:
            company_data = data['hits']['hits'][0]['_source']['Vrvirksomhed']

            # Extract the business type (correct field for business type)
            virksomhed_metadata = company_data.get('virksomhedMetadata', {})
            business_type_data = virksomhed_metadata.get('nyesteVirksomhedsform', {})
            business_type = business_type_data.get('langBeskrivelse', 'Anpartsselskab')

            # Handle beliggenhedsadresse, which might be a list
            beliggenhedsadresse = company_data.get('beliggenhedsadresse', [])
            if isinstance(beliggenhedsadresse, list) and beliggenhedsadresse:
                beliggenhedsadresse = beliggenhedsadresse[-1]  # Take the first entry
            
            # Extract advertising protection
            advertising_protection = "Yes" if company_data.get('reklamebeskyttet', False) else "No"    

            # Extract general information
            general_info = {
                "company_name": virksomhed_metadata.get('nyesteNavn', {}).get('navn', 'N/A'),
                "cvr_number": company_data.get('cvrNummer', 'N/A'),
                "address": self._format_address(beliggenhedsadresse),
                "postal_code": str(beliggenhedsadresse.get('postnummer', 'N/A')),
                "city": beliggenhedsadresse.get('postdistrikt', 'N/A'),
                "start_date": virksomhed_metadata.get('stiftelsesDato', 'N/A'),
                "business_type": business_type,
                "advertising_protection": advertising_protection,
                "status": virksomhed_metadata.get('sammensatStatus', 'Normal')
            }

            return general_info

        except KeyError as e:
            raise Exception(f"Key error accessing the company data: {str(e)}")
        except Exception as e:
            raise Exception(f"An error occurred while parsing the company data: {str(e)}")









    def _format_address(self, address_data: dict) -> str:
        """
        Helper method to format the company address.
        """
        # Handle lists properly and ensure safe access to address fields
        if isinstance(address_data, list) and address_data:
            address_data = address_data[0]  # Take the first entry if it’s a list

        vejnavn = str(address_data.get('vejnavn', 'N/A')).strip()  # Convert to string and strip
        husnummer = str(address_data.get('husnummerFra', '')).strip()  # Convert to string and strip
        postnummer = str(address_data.get('postnummer', 'N/A')).strip()  # Convert to string and strip
        postdistrikt = str(address_data.get('postdistrikt', 'N/A')).strip()  # Convert to string and strip
        kommune = str(address_data.get('kommune', {}).get('navn', '')).strip()  # Convert to string and strip

        # Combine address parts
        address_parts = [vejnavn, husnummer, postnummer, postdistrikt, kommune]
        formatted_address = ', '.join(part for part in address_parts if part)

        return formatted_address if formatted_address else "N/A"

    
    
    
    
    #not working correctly    
    def get_company_data_by_cvr_id(self, cvr_id: int) -> dict:
        """
        Searches for a company by CVR ID and returns all relevant data about the company.
        """
        query = {
            "query": {
                "match": {
                    "Vrvirksomhed.cvrNummer": cvr_id
                }
            }
        }

        response = requests.post(
            f"{self.base_url}",
            auth=self.auth,
            json=query
        )

        if response.status_code != 200:
            raise Exception(f"ElasticSearch query failed with status code {response.status_code}")

        data = response.json()
        print("0")

        total_hits = data['hits']['total']
        if isinstance(total_hits, dict):
            total_hits = total_hits.get('value', 0)
        elif isinstance(total_hits, int):
            total_hits = total_hits
        else:
            raise Exception("Unexpected format for total hits")

        if total_hits == 0:
            raise Exception(f"No company found with CVR ID: {cvr_id}")

        try:
            company_data = data['hits']['hits'][0]['_source']['Vrvirksomhed']

            # Safely access virksomhed_metadata
            virksomhed_metadata = company_data.get('virksomhedMetadata', {})
            if isinstance(virksomhed_metadata, list):
                virksomhed_metadata = virksomhed_metadata[0] if virksomhed_metadata else {}

            # Safely access post_address
            post_address = company_data.get('postadresse', [])
            if not post_address:
                post_address = company_data.get('beliggenhedsadresse', [])
                print(f"Raw beliggenhedsadresse data: {post_address}")  # Debugging

            if isinstance(post_address, list) and post_address:
                post_address = post_address[0]
            else:
                post_address = {}

            # Safely access contact_info
            contact_info = company_data.get('telefonNummer', [])
            if isinstance(contact_info, list) and contact_info:
                contact_info = contact_info[0]
            else:
                contact_info = {}

            # Safely access employee_data
            employee_data = company_data.get('aarsbeskaeftigelse', [])
            if isinstance(employee_data, list) and employee_data:
                employee_data = employee_data[-1]  # Latest employee data
            else:
                employee_data = {}

            # Safely access hovedbranche
            industry_info = company_data.get('hovedbranche', [])
            if isinstance(industry_info, list) and industry_info:
                industry_info = industry_info[0]
            else:
                industry_info = {}

            # Registered capital handling
            registered_capital = virksomhed_metadata.get('registreretKapital', [])
            if isinstance(registered_capital, list) and registered_capital:
                registered_capital = registered_capital[0]
            if isinstance(registered_capital, dict):
                registered_capital = registered_capital.get('kapital', 'N/A')
            elif isinstance(registered_capital, str):
                registered_capital = registered_capital
            else:
                registered_capital = "N/A"

            print(f"registered_capital after conversion: {registered_capital}")


            # Return structured company data
            return {
                "cvr_id": company_data.get('cvrNummer'),
                "company_name": virksomhed_metadata.get('nyesteNavn', {}).get('navn', "N/A"),
                "company_type": virksomhed_metadata.get('selskabsform', {}).get('langBeskrivelse', "N/A"),
                "registration_date": virksomhed_metadata.get('stiftelsesDato', "N/A"),
                "termination_date": virksomhed_metadata.get('ophørsDato', "N/A"),
                "status": virksomhed_metadata.get('sammensatStatus', "N/A"),
                "address": self._format_address(post_address),
                "industry_code": industry_info.get('branchetekst', "N/A"),
                "contact_information": contact_info.get('kontaktoplysning', "N/A"),
                "number_of_employees": employee_data.get('antalAnsatte', "N/A"),
                "personnel_circle": ', '.join([p.get('navn', 'N/A') for p in company_data.get('personkreds', [])]),
                "subscription_rule": company_data.get('tegningsregel', "N/A"),
                "registered_capital": registered_capital
            }
        except KeyError as e:
            raise Exception(f"Key error accessing the company data: {str(e)}")
        except Exception as e:
            raise Exception(f"An error occurred while parsing the company data: {str(e)}")

        """
    def _format_address(self, address_data: dict) -> str:
        """
        #Helper method to format the company address.
        """
        if isinstance(address_data, list) and len(address_data) > 0:
            address_data = address_data[0]  # If address is a list, take the first item

        # Use .get() to safely access address components, and avoid including empty strings
        vejnavn = address_data.get('vejnavn', '').strip()
        husnummer = address_data.get('husnummerFra', '').strip()
        bogstav = address_data.get('bogstavFra', '').strip()
        etage = address_data.get('etage', '').strip()
        postnummer = str(address_data.get('postnummer', '')).strip()
        postdistrikt = address_data.get('postdistrikt', '').strip()
        kommune = address_data.get('kommune', {}).get('kommuneNavn', '').strip()

        # Construct the full address
        address_parts = [vejnavn, husnummer + bogstav, etage, postnummer + ' ' + postdistrikt, kommune]
        formatted_address = ', '.join(part for part in address_parts if part)

        # Return the formatted address or "N/A" if it's empty
        return formatted_address if formatted_address else "N/A"
    """


        


