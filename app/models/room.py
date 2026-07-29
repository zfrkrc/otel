from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, func, ForeignKey, Date
from app.database import Base

class RoomType(Base):
    __tablename__ = "room_types"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    base_price = Column(Float, nullable=False)
    capacity = Column(Integer, default=2)
    amenities = Column(Text, nullable=True)

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id", ondelete="SET NULL"), nullable=True)
    room_number = Column(String(20), nullable=False)
    floor = Column(Integer, nullable=True)
    status = Column(String(30), default="available")
    notes = Column(Text, nullable=True)

class SeasonalPrice(Base):
    __tablename__ = "seasonal_prices"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id", ondelete="CASCADE"), nullable=False)
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    price = Column(Float, nullable=False)
    name = Column(String(100), nullable=True)
