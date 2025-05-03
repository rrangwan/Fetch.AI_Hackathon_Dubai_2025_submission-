from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

PORT = os.getenv("PORT", 8000)
if not PORT:
    raise ValueError("PORT variable is not set in the .env file")

# Get the SEED variable from the .env file
SEED = os.getenv("SEED")
if not SEED:
    raise ValueError("SEED variable is not set in the .env file")

ASI1_MODEL = os.getenv("ASI1_MODEL", "asi1-mini")
if not ASI1_MODEL:
    raise ValueError("ASI1_MODEL variable is not set in the .env file")

ASI1_API_KEY = os.getenv("ASI1_API_KEY")
if not ASI1_API_KEY:
    raise ValueError("ASI1_API_KEY variable is not set in the .env file")

MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
if not MAX_TOKENS:
    raise ValueError("MAX_TOKENS variable is not set in the .env file")

WAVER_ADDRESS = os.getenv("WAVER_ADDRESS")
if not WAVER_ADDRESS:
    raise ValueError("WAVER_ADDRESS variable is not set in the .env file")