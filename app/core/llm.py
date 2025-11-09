# Commented out Mistral AI implementation
# from langchain_mistralai.chat_models import ChatMistralAI

# Google Gemini API implementation
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import time

class RateLimitError(Exception):
    """Custom exception for rate limit errors"""
    pass

def get_llm():
    """Get a configured instance of the Google Gemini AI chat model"""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.7,
        convert_system_message_to_human=True,  # Required for Gemini
        max_output_tokens=8192,
        timeout=120,
        max_retries=5,
    )

# Legacy Mistral AI function (commented out)
# def get_mistral_llm():
#     """Get a configured instance of the Mistral AI chat model"""
#     load_dotenv()
#     api_key = os.getenv("MISTRAL_API_KEY")
#     if not api_key:
#         raise ValueError("MISTRAL_API_KEY not found in environment variables")
#     
#     return ChatMistralAI(
#         temperature=0.7,
#         model="mistral-medium-latest",
#         api_key=api_key,
#         timeout=120,  # Increased timeout to 120 seconds
#         max_retries=5,  # Enable built-in retry mechanism
#     ) 