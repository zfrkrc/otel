from sqlalchemy import Column, Integer, String, Float, Date, DateTime, func, Text, ForeignKey
from app.database import Base

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id", ondelete="SET NULL"), nullable=True)
    guest_id = Column(Integer, ForeignKey("guests.id", ondelete="SET NULL"), nullable=True)
    invoice_no = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    tax = Column(Float, default=0)
    total = Column(Float, nullable=False)
    status = Column(String(30), default="pending")
    payment_method = Column(String(50), nullable=True)
    due_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
