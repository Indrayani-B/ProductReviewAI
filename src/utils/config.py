from dotenv import load_dotenv
import os

load_dotenv()

#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH        = os.getenv("DB_PATH", "data/reviews.db")
MODEL_DIR      = os.getenv("MODEL_DIR", "models/")