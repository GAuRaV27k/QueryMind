from exa_py import Exa
import os 
from dotenv import load_dotenv
load_dotenv()

exa_api_key = os.getenv("EXA_API") or os.getenv("EXA_API_KEY")
exa_client = Exa(api_key=exa_api_key)
