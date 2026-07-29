from sqlalchemy import Column, Integer, String, Float, Text, DateTime, func, ForeignKey
from app.database import Base

class InventoryItem(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    quantity = Column(Integer, default=0)
    min_quantity = Column(Integer, default=0)
    unit = Column(String(50), nullable=True)
    unit_price = Column(Float, nullable=True)
    supplier = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
