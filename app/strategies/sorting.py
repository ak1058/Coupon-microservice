# app/strategies/sorting.py
from typing import List
from ..schemas.cart import ApplicableCoupon

class SortingStrategy:
    """Different strategies to sort applicable coupons"""
    
    @staticmethod
    def sort_by_absolute_discount(coupons: List[ApplicableCoupon]) -> List[ApplicableCoupon]:
        """Sort by absolute discount amount (₹500 > ₹300)"""
        return sorted(coupons, key=lambda x: x.discount, reverse=True)
    
    @staticmethod
    def sort_by_percentage_discount(coupons: List[ApplicableCoupon]) -> List[ApplicableCoupon]:
        """Sort by percentage of cart total (20% > 15%)"""
        return sorted(coupons, key=lambda x: x.discount_percentage or 0, reverse=True)
    
    @staticmethod
    def sort_by_coupon_type_priority(coupons: List[ApplicableCoupon]) -> List[ApplicableCoupon]:
        """Sort by coupon type priority (BxGy > Product-wise > Cart-wise)"""
        type_priority = {"bxgy": 3, "product-wise": 2, "cart-wise": 1}
        return sorted(
            coupons, 
            key=lambda x: (type_priority.get(x.type, 0), x.discount), 
            reverse=True
        )
    
    @staticmethod
    def sort_hybrid(coupons: List[ApplicableCoupon]) -> List[ApplicableCoupon]:
        """Hybrid sorting: Balance between absolute discount and percentage"""
        def calculate_score(coupon):
            # 70% weight to absolute discount, 30% to percentage
            absolute_score = coupon.discount
            percentage_score = (coupon.discount_percentage or 0) * 10  # Scale up percentage
            return (absolute_score * 0.7) + (percentage_score * 0.3)
        
        return sorted(coupons, key=calculate_score, reverse=True)