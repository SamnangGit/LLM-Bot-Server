from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os

load_dotenv()

class DBConnector:

    @staticmethod
    def init_engine():

        # Fetching the environment variables for database connection
        DB_CONNECTION = os.getenv("DB_CONNECTION", "postgresql")
        DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_DATABASE = os.getenv("DB_DATABASE", "dev_llm_bot")
        DB_USERNAME = os.getenv("DB_USERNAME", "username")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "")

        if not DB_PASSWORD:
            raise ValueError("No database password provided in environment variables.")

        SQLALCHEMY_DATABASE_URL = f"{DB_CONNECTION}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

        engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)  # Use echo=True to see SQL logs during development
        return engine;
