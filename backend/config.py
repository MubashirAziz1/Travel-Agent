"""Environment loading and client initialization."""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from pathlib import Path
from typing import List, Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"


class BaseConfigSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", str(ENV_FILE_PATH)],
        extra="ignore",
        frozen=True,
        env_nested_delimiter="__",
        case_sensitive=False,
    )

class DuffelSettings(BaseConfigSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", str(ENV_FILE_PATH)],
        env_prefix="DUFFEL__",
        extra="ignore",
        frozen=True,
        case_sensitive=False,
    )
    
    base_url: str 
    api_key: str 


   
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


if not all([GOOGLE_API_KEY]):
    raise ValueError("Required API keys missing: GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=GOOGLE_API_KEY,
)
