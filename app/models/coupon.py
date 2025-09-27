from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from ..database import Base
import uuid

class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String, nullable=False)  # cart-wise, product-wise, bxgy
    title = Column(String, nullable=False)
    description = Column(String)
    details = Column(JSON, nullable=False)  # Store type-specific details
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Bonus: expiration
    usage_limit = Column(Integer, nullable=True)  # Max times coupon can be used
    usage_count = Column(Integer, default=0)  # Times coupon has been used