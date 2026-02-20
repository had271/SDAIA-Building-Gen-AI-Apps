import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "openrouter/stepfun/step-3.5-flash:free")
    # Add other configuration as needed
