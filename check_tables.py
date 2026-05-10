#Prova con alembic
import psycopg2
from os import getenv
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = getenv("DATABASE_URL")


conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("""
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'categories';
""")


conn.close()
