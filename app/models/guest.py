from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean
from app.database import Base

class Guest(Base):
    __tablename__ = "guests"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    id_card = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    nationality = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    is_blacklisted = Column(Boolean, default=False)
    total_visits = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
