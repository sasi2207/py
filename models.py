# models.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    # The first parameter "password" tells SQLAlchemy the actual DB column name
    hashed_password = Column("password", String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), default="student", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))