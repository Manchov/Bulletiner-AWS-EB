# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
