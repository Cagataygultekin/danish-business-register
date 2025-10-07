import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CVR_API_URL: str
    CVR_API_USERNAME: str
    CVR_API_PASSWORD: str
    ELASTICSEARCH_VERSION: str

    class Config:
        env_file = ".env"  # Optional: You can load a .env file for local development if needed.
