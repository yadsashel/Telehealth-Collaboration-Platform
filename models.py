import os
from sqlalchemy import Column, String, Integer, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv 

# Initialize the database
load_dotenv()

Base = declarative_base()
DATABASE_URL = os.getenv("DATABASE_URL")

# Define the models
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    user_type = Column(String(20), nullable=False)
    mfa_code = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


# Engine and sessionmaker
engine = create_engine(DATABASE_URL, echo=True)
SQLASession = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(engine)