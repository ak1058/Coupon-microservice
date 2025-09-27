# app/repositories/coupon_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.coupon import Coupon
from ..schemas.coupon import CouponCreateRequest, CouponUpdateRequest
from datetime import datetime

class CouponRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_coupon(self, coupon_data: CouponCreateRequest) -> Coupon:
        """Create a new coupon"""
        coupon = Coupon(
            type=coupon_data.type.value,
            title=coupon_data.title,
            description=coupon_data.description,
            details=coupon_data.details.dict(),
            expires_at=coupon_data.expires_at,
            usage_limit=coupon_data.usage_limit
        )
        self.db.add(coupon)
        self.db.commit()
        self.db.refresh(coupon)
        return coupon
    
    def get_coupon_by_id(self, coupon_id: str) -> Optional[Coupon]:
        """Get coupon by ID"""
        return self.db.query(Coupon).filter(Coupon.id == coupon_id).first()
    
    def get_all_coupons(self) -> List[Coupon]:
        """Get all coupons"""
        return self.db.query(Coupon).filter(Coupon.is_active == True).all()
    
    def get_active_coupons(self) -> List[Coupon]:
        """Get all active and non-expired coupons"""
        now = datetime.utcnow()
        return self.db.query(Coupon).filter(
            Coupon.is_active == True,
            (Coupon.expires_at.is_(None) | (Coupon.expires_at > now))
        ).all()
    
    def update_coupon(self, coupon_id: str, update_data: CouponUpdateRequest) -> Optional[Coupon]:
        """Update coupon"""
        coupon = self.get_coupon_by_id(coupon_id)
        if not coupon:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(coupon, field, value)
        
        coupon.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(coupon)
        return coupon
    
    def delete_coupon(self, coupon_id: str) -> bool:
        """Soft delete coupon"""
        coupon = self.get_coupon_by_id(coupon_id)
        if not coupon:
            return False
        
        coupon.is_active = False
        coupon.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def increment_usage_count(self, coupon_id: str) -> bool:
        """Increment usage count when coupon is applied"""
        coupon = self.get_coupon_by_id(coupon_id)
        if not coupon:
            return False
        
        coupon.usage_count += 1
        self.db.commit()
        return True