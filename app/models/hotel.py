from sqlalchemy import Column, Integer, String, Text, DateTime, func, Boolean, ForeignKey, Date, Float
from app.database import Base

class Hotel(Base):
    __tablename__ = "hotels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    token_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)
class HousekeepingTask(Base):
    __tablename__ = "housekeeping"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    assigned_to = Column(String(100), nullable=True)
    status = Column(String(30), default="pending")
    priority = Column(String(20), default="normal")
    notes = Column(Text, nullable=True)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class RestaurantOrder(Base):
    __tablename__ = "restaurant_orders"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    guest_id = Column(Integer, ForeignKey("guests.id", ondelete="SET NULL"), nullable=True)
    items = Column(Text, nullable=True)
    total = Column(Float, default=0)
    status = Column(String(30), default="pending")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    price = Column(Float, nullable=False)
    available = Column(Boolean, default=True)

class HotelIssue(Base):
    __tablename__ = "hotel_issues"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(30), default="open")
    priority = Column(String(20), default="normal")
    reported_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)
