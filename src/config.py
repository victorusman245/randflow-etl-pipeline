import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID')
SERVICE_ACCOUNT_FILE = BASE_DIR / os.getenv('SERVICE_ACCOUNT_FILE')
RAW_DIR = BASE_DIR / 'data' / 'raw'

DB_URL = URL.create(
    'postgresql+psycopg2',
    username=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', 5432)),
    database=os.getenv('DB_NAME'),
)