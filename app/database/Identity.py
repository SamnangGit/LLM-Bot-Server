from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Identity(Base):
    __tablename__ = "identity"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, nullable=False)