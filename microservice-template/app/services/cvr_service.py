import requests
from app.config import Settings
from dotenv import load_dotenv
import os
import json
import re

from app.dtos.cvr_dto import OwnershipResponse, OwnershipInfo


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






    def get_possible_ownership_info_by_cvr_id(self, cvr_id: int) -> dict:
        """
        Searches for a company by CVR ID and returns its possible legal and beneficial ownership information.
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
        
        try:
            hits = data.get('hits', {}).get('hits', [])
            if not hits:
                raise ValueError("No hits found in response")

            company_data = hits[0].get('_source', {}).get('Vrvirksomhed', {})
            company_name = company_data.get('virksomhedMetadata', {}).get('nyesteNavn', {}).get('navn', 'N/A')
            cvr_number = company_data.get('cvrNummer', 'N/A')
            possible_legal_owners, possible_beneficial_owners = [], []

            # Extract possible ownership data
            participant_relations = company_data.get('deltagerRelation', [])
            organization_indicators = {"A/S", "ApS", "Inc.", "LLC", "S.A.", "P/S", "Ltd.", "I/S", "INC."}

            for relation in participant_relations:
                if relation is None or relation.get('deltager') is None:
                    continue

                deltagertype = relation.get('deltager', {}).get('enhedstype', "")
                navne_list = relation.get('deltager', {}).get('navne', [])
                for navn_entry in navne_list:
                    owner_name = navn_entry.get('navn', "Unknown")
                    
                    if any(indicator in owner_name for indicator in organization_indicators) or deltagertype == "VIRKSOMHED":
                        possible_legal_owners.append(owner_name)
                    else:
                        possible_beneficial_owners.append(owner_name)

            result = {
                "cvr_number": cvr_number,
                "company_name": company_name,
                "possible_legal_owners": list(dict.fromkeys(possible_legal_owners)),
                "possible_beneficial_owners": list(dict.fromkeys(possible_beneficial_owners))
            }
            return result

        except Exception as e:
            raise Exception(f"An error occurred while parsing the company data: {str(e)}")






    def get_key_individuals_by_cvr_id(self, cvr_id: int) -> dict:
        """
        Searches for a company by CVR ID and returns key individuals like Management,
        Board of Directors, Founders, and Fully Liable Partners.
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
        hits = data.get('hits', {}).get('hits', [])

        if not hits:
            raise ValueError("No hits found for the provided CVR ID")

        company_data = hits[0].get('_source', {}).get('Vrvirksomhed', {})

        key_individuals = {
            "management": [],
            "board_of_directors": [],
            "founders": [],
            "fully_liable_partners": []
        }

        # Look for key individual roles in `deltagerRelation`
        ledelsesorgan_data = company_data.get('deltagerRelation', [])
        for entry in ledelsesorgan_data:
            organisations = entry.get('organisationer', [])
            for org in organisations:
                hovedtype = org.get('hovedtype', None)
                
                # Skip unwanted hovedtype values
                if hovedtype not in ["LEDELSESORGAN", "STIFTERE", "FULDT_ANSVARLIG_DELTAGERE"]:
                    print(f"Skipping hovedtype: {hovedtype}")  # Log for debugging
                    continue
                       
                # Set role name and extract name and address details
                role_name = org.get('organisationsNavn', [{}])[0].get('navn', 'Unknown') if org.get('organisationsNavn') else 'Unknown'
                individuals = entry.get('deltager', {}).get('navne', [{}])[0].get('navn', 'Unknown') if entry.get('deltager', {}).get('navne') else 'Unknown'

                # Check for secret address
                if entry.get('deltager', {}).get('adresseHemmelig', False):
                    address = "Secret Address"
                else:
                    # Extract address based on the available fields
                    beliggenhedsadresse = entry.get('deltager', {}).get('beliggenhedsadresse', [])
                    address = "Unknown address"
                    if beliggenhedsadresse and isinstance(beliggenhedsadresse, list):
                        address_data = beliggenhedsadresse[0] if beliggenhedsadresse[0] is not None else {}
                        if address_data.get('fritekst'):
                            # Handle multi-line addresses in `fritekst`
                            address = address_data['fritekst'].replace('\n', ', ').strip()
                        else:
                            # Safely get each part of the address, avoiding None values
                            vejnavn = str(address_data.get('vejnavn', '') or '').strip()
                            husnummer = str(address_data.get('husnummerFra', '') or '').strip()
                            postnummer = str(address_data.get('postnummer', '') or '').strip()
                            postdistrikt = str(address_data.get('postdistrikt', '') or '').strip()
                            kommune = str((address_data.get('kommune') or {}).get('kommuneNavn', '') or '').strip()
                            landekode = str(address_data.get('landekode', '') or '').strip()

                            # Filter out empty strings and join remaining parts
                            address_parts = [vejnavn, husnummer, postnummer, postdistrikt, kommune, landekode]
                            address = ', '.join(part for part in address_parts if part) if any(address_parts) else "Unknown address"

                print("hovedtype:",hovedtype)
                print("role_name:",role_name)            
                # Categorize based on the `hovedtype` field
                if hovedtype == "LEDELSESORGAN":
                    if role_name == "Bestyrelse":
                        key_individuals["board_of_directors"].append({"name": individuals, "address": address})
                    elif role_name == "Direktion":
                        key_individuals["management"].append({"name": individuals, "address": address})
                elif hovedtype == "STIFTERE":
                    key_individuals["founders"].append({"name": individuals, "address": address})
                elif hovedtype == "FULDT_ANSVARLIG_DELTAGERE":
                    key_individuals["fully_liable_partners"].append({"name": individuals, "address": address})

        return key_individuals




    def get_ownership_info(self, cvr_id: int) -> OwnershipResponse:
        query = {
            "query": {
                "match": {
                    "Vrvirksomhed.cvrNummer": cvr_id
                }
            }
        }

        response = requests.post(f"{self.base_url}", auth=self.auth, json=query)
        if response.status_code != 200:
            raise Exception(f"Query failed with status code {response.status_code}")

        data = response.json()
        company_data = data['hits']['hits'][0]['_source']['Vrvirksomhed']

        legal_owners, beneficial_owners, terminated_owners = [], [], []

        for relation in company_data.get('deltagerRelation', []):
            if relation.get('deltager') is None:
                continue
            
            navne = relation.get('deltager', {}).get('navne', [])
            organisationer = relation.get('organisationer', [])

            owner_name = None
            for navn_entry in navne:
                owner_name = navn_entry['navn']  # Get the last name in the sequence

            # Format the owner's address
            address = self._format_owner_address(relation.get("deltager", {}).get("beliggenhedsadresse", []))

            for org in organisationer:
                org_name = org.get('organisationsNavn', [{}])[0].get('navn')
                if org_name == "EJERREGISTER":
                    owner_type = "Legal"
                elif org_name == "Reelle ejere":
                    owner_type = "Beneficial"
                else:
                    continue

                # Process ownership attributes
                ownership_percentage, voting_percentage, start_date, end_date = (
                    self._get_ownership_details(org)
                )

                ownership_info = OwnershipInfo(
                    owner_name=owner_name,
                    ownership_percentage=ownership_percentage,
                    voting_percentage=voting_percentage,
                    ownership_type="Terminated" if end_date else owner_type,
                    start_date=start_date,
                    end_date=end_date,
                    address=address
                )

                if end_date:  # Classify as terminated if end_date is present
                    terminated_owners.append(ownership_info)
                elif owner_type == "Legal":
                    legal_owners.append(ownership_info)
                else:
                    beneficial_owners.append(ownership_info)

        return OwnershipResponse(
            cvr_number=cvr_id,
            company_name=company_data.get('virksomhedMetadata', {}).get('nyesteNavn', {}).get('navn', 'N/A'),
            legal_owners=legal_owners,
            beneficial_owners=beneficial_owners,
            terminated_owners=terminated_owners
        )

    def _format_owner_address(self, address_data: list) -> str:
        """
        Formats the address for a single owner using available information.
        If `fritekst` is provided, it uses it directly; otherwise, it constructs the address.
        """
        if not address_data:
            return "N/A"

        # Use the most recent address (last in list)
        latest_address = address_data[-1] if address_data else {}

        # Use `fritekst` if available
        if latest_address.get("fritekst"):
            formatted_address = latest_address["fritekst"].replace("\n", ", ").strip()
        else:
            # Construct address manually if `fritekst` is not available
            vejnavn = str(latest_address.get("vejnavn") or "").strip()
            husnummer = str(latest_address.get("husnummerFra") or "").strip()
            bogstav = str(latest_address.get("bogstavFra") or "").strip()
            etage = str(latest_address.get("etage") or "").strip()
            sidedoer = str(latest_address.get("sidedoer") or "").strip()
            postnummer = str(latest_address.get("postnummer") or "").strip()
            postdistrikt = str(latest_address.get("postdistrikt") or "").strip()
            
            kommune = str(latest_address.get("kommune", {}).get("kommuneNavn") or "").strip() \
                if isinstance(latest_address.get("kommune"), dict) else ""
            
            address_parts = [
                vejnavn,
                f"{husnummer}{bogstav}" if husnummer or bogstav else "",
                etage,
                sidedoer,
                f"{postnummer} {postdistrikt}".strip() if postnummer or postdistrikt else "",
                kommune
            ]

            formatted_address = ', '.join(part for part in address_parts if part) if address_parts else "N/A"

        # Append the country code if available
        landekode = latest_address.get("landekode")
        if landekode:
            formatted_address = f"{formatted_address}, {landekode}"

        return formatted_address if formatted_address else "N/A"




    def _get_ownership_details(self, organisation):
        """
        Extracts ownership details including ownership percentage, voting percentage,
        start date, and end date (for terminated owners).
        """
        ownership_percentage = voting_percentage = start_date = end_date = None

        for medlemsData in organisation.get("medlemsData", []):
            for attr in medlemsData.get("attributter", []):
                if attr["type"] == "EJERANDEL_PROCENT":
                    for value in attr["vaerdier"]:
                        # Capture ownership percentage, start date, and end date
                        ownership_percentage = value["vaerdi"]
                        start_date = value["periode"].get("gyldigFra")
                        end_date = value["periode"].get("gyldigTil")
                        
                elif attr["type"] == "EJERANDEL_STEMMERET_PROCENT":
                    for value in attr["vaerdier"]:
                        # Capture voting percentage for the corresponding period
                        if start_date == value["periode"].get("gyldigFra") and end_date == value["periode"].get("gyldigTil"):
                            voting_percentage = value["vaerdi"]

        return ownership_percentage, voting_percentage, start_date, end_date

   

    def _get_current_attribute_value(self, organisation, attribute_type):
        """
        Helper to fetch a specific attribute value (e.g., 'EJERANDEL_PROCENT') and its start date (gyldigFra)
        from the organisation data. Only considers the attribute if 'gyldigTil' is null, meaning the owner is current.
        """
        for medlemsData in organisation.get("medlemsData", []):
            for attr in medlemsData.get("attributter", []):
                if attr["type"] == attribute_type:
                    # Check if 'gyldigTil' is null for current ownership
                    for value in attr["vaerdier"]:
                        if value["periode"].get("gyldigTil") is None:
                            return value["vaerdi"], value["periode"].get("gyldigFra")
        return None, None  # Return None for both if not found





from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

class PDFService:
    def __init__(self):
        self.base_url = "https://datacvr.virk.dk/gateway/pdf/hentVirksomhedsvisningSomPdf"
        self.download_dir = os.path.abspath("./downloads")  # Use absolute path for clarity
        os.makedirs(self.download_dir, exist_ok=True)  # Ensure download directory exists

        # Setup Selenium WebDriver with Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # Headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.69 Safari/537.36")
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,  # Ensure PDFs are downloaded directly
        })

        # ChromeDriver configuration
        # The only thing need to change depends on the device
        service = Service("C:/Users/cagat/OneDrive/Masaüstü/learning_scrapping/for_selenium/chromedriver-win64/chromedriver.exe")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def wait_for_pdf_download(self, expected_filename: str, timeout: int = 60) -> str:
        """
        Waits for the PDF download to complete and returns the full file path.
        """
        for _ in range(timeout):
            # Check if the file or partially downloaded file exists
            for filename in os.listdir(self.download_dir):
                if filename.startswith(expected_filename) and not filename.endswith(".crdownload"):
                    return os.path.join(self.download_dir, filename)
            time.sleep(1)  # Wait for a second before retrying
        raise Exception("PDF download timed out or file not found.")

    def download_pdf(self, cvr_id: int) -> dict:
        """
        Downloads the PDF for a given CVR ID and waits for it to complete.

        Args:
            cvr_id (int): The CVR ID of the company.

        Returns:
            dict: A dictionary with file path, file name, and a message.
        """
        try:
            url = f"{self.base_url}?cvrnummer={cvr_id}&locale=en"
            print(f"Navigating to URL: {url}")
            self.driver.get(url)
            print("URL loaded in browser. Waiting for PDF download...")

            # Wait for the file to download
            expected_filename = f"{cvr_id}+-+Full+view"
            downloaded_file_path = self.wait_for_pdf_download(expected_filename)
            print(f"PDF downloaded to: {downloaded_file_path}")

            # Success response
            return {
                "file_path": downloaded_file_path,
                "file_name": os.path.basename(downloaded_file_path),
                "message": "PDF downloaded successfully."
            }

        except Exception as e:
            print(f"Error downloading PDF: {e}")
            raise Exception(f"Error downloading PDF: {e}")

    def close_driver(self):
        """
        Manually close the WebDriver when no longer needed.
        """
        try:
            self.driver.quit()
        except Exception as e:
            print(f"Error closing the driver: {e}")


















    
    
    
    #Doesn't work part starts here
    ###
    ###
    ###
    
    def get_person_info_by_name(self, name: str) -> dict:
        """
        Searches for a person by name and returns their full name.
        """
        query = {
            "query": {
                "match": {
                    "Vrvirksomhed.personer.navn": name
                }
            }
        }

        response = requests.post(
            f"{self.base_url}/person-search-endpoint",  # Update with actual endpoint URL
            auth=self.auth,
            json=query
        )

        if response.status_code != 200:
            raise Exception(f"Person search query failed with status code {response.status_code}")

        data = response.json()

        # Handle parsing of person data here
        person_data = data['hits']['hits'][0]['_source']['Vrvirksomhed']['personer']

        try:
            full_name = person_data['navn']
            return {
                "full_name": full_name
            }
        except KeyError as e:
            raise Exception(f"Key error accessing person data: {str(e)}")
        except Exception as e:
            raise Exception(f"An error occurred while parsing person data: {str(e)}")

    
    
    

    
    
    
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


        


