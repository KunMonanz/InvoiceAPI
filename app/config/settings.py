import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads") 
FILE_AGE_THRESHOLD: int = 86400 

GOOGLE_CLIENT_ID: str | None = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET_KEY: str | None = os.getenv("GOOGLE_SECRET_KEY")
GOOGLE_SESSION_SECRET: str | None = os.getenv("GOOGLE_SESSION_SECRET") 

JWT_SECRET_KEY: str | None = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM: str | None = os.getenv("JWT_ALGORITHM")  
