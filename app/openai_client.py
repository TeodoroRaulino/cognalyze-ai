import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

def get_client() -> AsyncOpenAI:
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY não definido no ambiente.")
    return AsyncOpenAI(api_key=openai_api_key)

def get_model(override: str | None = None) -> str:
    return override or openai_model
