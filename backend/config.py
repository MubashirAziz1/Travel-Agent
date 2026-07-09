"""Environment loading and client initialization."""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env'))
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


if not all([GOOGLE_API_KEY]):
    raise ValueError("Required API keys missing: GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=GOOGLE_API_KEY,
)