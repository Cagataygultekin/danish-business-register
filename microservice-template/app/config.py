import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CVR_API_URL: str
    CVR_API_USERNAME: str
    CVR_API_PASSWORD: str
    ELASTICSEARCH_VERSION: str

    class Config:
        env_file = ".env"  # Optional: You can load a .env file for local development if needed.


"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CVR_API_URL: str = "http://distribution.virk.dk:80/cvr-permanent/_search"  # Replace with actual URL
    CVR_API_USERNAME: str = "Legalian_CVR_I_SKYEN"             # Replace with actual username
    CVR_API_PASSWORD: str = "a13b0263-e68c-4ede-bf92-1e4056d77ec3"             # Replace with actual password
    ELASTICSEARCH_VERSION: str = "6.8.16"               # Specify the ElasticSearch version

    class Config:
        env_file = ".env"  # Load environment variables from a .env file if present

settings = Settings()
"""
"""
import os

EXAMPLE_ENV_VARIABLE = os.environ.get('EXAMPLE_ENV_VARIABLE')
assert EXAMPLE_ENV_VARIABLE is not None

"""

