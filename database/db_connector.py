from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnector:
    def __init__(self):
        self.engine = None
        self.Session = None
        self._initialize_connection()

    def _initialize_connection(self):
        """Initialize database connection using environment variables."""
        try:
            DB_USER = os.getenv('DB_USER', 'root')
            DB_PASSWORD = os.getenv('DB_PASSWORD', '')
            DB_HOST = os.getenv('DB_HOST', 'localhost')
            DB_PORT = os.getenv('DB_PORT', '3306')
            DB_NAME = os.getenv('DB_NAME', 'buses_db')

            DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

            self.engine = create_engine(
                DATABASE_URL,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800
            )

            self.Session = sessionmaker(bind=self.engine)

        except Exception as e:
            raise Exception(f"Failed to initialize database connection: {str(e)}")

    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def create_tables(self):
        """Create all tables in the database."""
        from .models import Base
        try:
            Base.metadata.create_all(self.engine)
            print("All tables created successfully")
        except Exception as e:
            raise Exception(f"Failed to create tables: {str(e)}")

    def drop_tables(self):
        """Drop all tables in the database."""
        from .models import Base
        try:
            Base.metadata.drop_all(self.engine)
            print("All tables dropped successfully")
        except Exception as e:
            raise Exception(f"Failed to drop tables: {str(e)}")

# Create a singleton instance
db = DatabaseConnector()
