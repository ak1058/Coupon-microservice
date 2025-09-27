# app/services/coupon_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..repositories.coupon_repository import CouponRepository
from ..services.discount_calculator import DiscountCalculator
from ..models.coupon import Coupon
from ..schemas.coupon import CouponCreateRequest, CouponUpdateRequest, CouponResponse
from ..schemas.cart import Cart, ApplicableCoupon, UpdatedCart, ApplicableCouponsResponse
from ..exceptions.custom_exceptions import (
    CouponNotFoundError, 
    CouponExpiredError, 
    CouponUsageLimitExceededError,
    CouponNotApplicableError
)
from ..strategies.sorting import SortingStrategy 

class CouponService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = CouponRepository(db)
        self.discount_calculator = DiscountCalculator()
    
    def create_coupon(self, coupon_data: CouponCreateRequest) -> CouponResponse:
        """Create a new coupon"""
        coupon = self.repository.create_coupon(coupon_data)
        return CouponResponse.from_orm(coupon)
    
    def get_coupon(self, coupon_id: str) -> CouponResponse:
        """Get coupon by ID"""
        coupon = self.repository.get_coupon_by_id(coupon_id)
        if not coupon:
            raise CouponNotFoundError(f"Coupon with id {coupon_id} not found")
        return CouponResponse.from_orm(coupon)
    
    def get_all_coupons(self) -> List[CouponResponse]:
        """Get all active coupons"""
        coupons = self.repository.get_all_coupons()
        return [CouponResponse.from_orm(coupon) for coupon in coupons]
    
    def update_coupon(self, coupon_id: str, update_data: CouponUpdateRequest) -> CouponResponse:
        """Update coupon"""
        coupon = self.repository.update_coupon(coupon_id, update_data)
        if not coupon:
            raise CouponNotFoundError(f"Coupon with id {coupon_id} not found")
        return CouponResponse.from_orm(coupon)
    
    def delete_coupon(self, coupon_id: str) -> bool:
        """Delete coupon"""
        success = self.repository.delete_coupon(coupon_id)
        if not success:
            raise CouponNotFoundError(f"Coupon with id {coupon_id} not found")
        return success
    
    def get_applicable_coupons(self, cart: Cart, sort_by: str = "discount") -> ApplicableCouponsResponse:
        """Get applicable coupons with different sorting options"""
        active_coupons = self.repository.get_active_coupons()
        applicable_coupons = []
        cart_total = sum(item.quantity * item.price for item in cart.items)
        
        # Step 1: Find all applicable coupons and calculate discounts
        for coupon in active_coupons:
            if self._is_coupon_valid(coupon) and self.discount_calculator.is_coupon_applicable(cart, coupon):
                discount = self.discount_calculator.calculate_discount(cart, coupon)
                if discount > 0:
                    # Calculate discount percentage of cart total
                    discount_percentage = (discount / cart_total * 100) if cart_total > 0 else 0
                    
                    applicable_coupons.append(ApplicableCoupon(
                        coupon_id=coupon.id,
                        type=coupon.type,
                        discount=round(discount, 2),
                        title=coupon.title,
                        description=coupon.description,
                        discount_percentage=round(discount_percentage, 2)
                    ))
        
        # Step 2: Apply sorting strategy
        if sort_by == "discount":
            applicable_coupons = SortingStrategy.sort_by_absolute_discount(applicable_coupons)
        elif sort_by == "percentage":
            applicable_coupons = SortingStrategy.sort_by_percentage_discount(applicable_coupons)
        elif sort_by == "type":
            applicable_coupons = SortingStrategy.sort_by_coupon_type_priority(applicable_coupons)
        elif sort_by == "hybrid":
            applicable_coupons = SortingStrategy.sort_hybrid(applicable_coupons)
        else:
            # Default to discount sorting if invalid sort_by provided
            applicable_coupons = SortingStrategy.sort_by_absolute_discount(applicable_coupons)
        
        # Step 3: Identify best coupon and calculate total savings
        best_coupon = applicable_coupons[0] if applicable_coupons else None
        total_savings = sum(coupon.discount for coupon in applicable_coupons)
        
        return ApplicableCouponsResponse(
            applicable_coupons=applicable_coupons,
            best_coupon=best_coupon,
            total_savings_potential=round(total_savings, 2)
        )


    def apply_coupon(self, coupon_id: str, cart: Cart) -> UpdatedCart:
        """Apply specific coupon to cart"""
        coupon = self.repository.get_coupon_by_id(coupon_id)
        if not coupon:
            raise CouponNotFoundError(f"Coupon with id {coupon_id} not found")
        
        if not self._is_coupon_valid(coupon):
            if coupon.expires_at and coupon.expires_at < datetime.utcnow():
                raise CouponExpiredError("Coupon has expired")
            if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
                raise CouponUsageLimitExceededError("Coupon usage limit exceeded")
        
        if not self.discount_calculator.is_coupon_applicable(cart, coupon):
            raise CouponNotApplicableError("Coupon is not applicable to this cart")
        
        # Apply the discount
        updated_cart = self.discount_calculator.apply_discount(cart, coupon)
        
        # Increment usage count
        self.repository.increment_usage_count(coupon_id)
        
        return updated_cart
    
    def _is_coupon_valid(self, coupon: Coupon) -> bool:
        """Check if coupon is valid (not expired, usage limit not exceeded)"""
        now = datetime.utcnow()
        
        # Check if coupon is active
        if not coupon.is_active:
            return False
        
        # Check expiration
        if coupon.expires_at and coupon.expires_at < now:
            return False
        
        # Check usage limit
        if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
            return False
        
        return True