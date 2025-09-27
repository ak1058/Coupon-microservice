# app/services/discount_calculator.py
from typing import Dict
from ..strategies import DiscountStrategy, CartWiseStrategy, ProductWiseStrategy, BxGyStrategy
from ..models.coupon import Coupon
from ..schemas.cart import Cart
from ..exceptions.custom_exceptions import UnsupportedCouponTypeError

class DiscountCalculator:
    """Service to calculate discounts using strategy pattern"""
    
    def __init__(self):
        self.strategies: Dict[str, DiscountStrategy] = {
            "cart-wise": CartWiseStrategy(),
            "product-wise": ProductWiseStrategy(),
            "bxgy": BxGyStrategy()
        }
    
    def register_strategy(self, coupon_type: str, strategy: DiscountStrategy):
        """Register a new discount strategy for extensibility"""
        self.strategies[coupon_type] = strategy
    
    def is_coupon_applicable(self, cart: Cart, coupon: Coupon) -> bool:
        """Check if coupon is applicable to cart"""
        if coupon.type not in self.strategies:
            raise UnsupportedCouponTypeError(f"Unsupported coupon type: {coupon.type}")
        
        strategy = self.strategies[coupon.type]
        return strategy.is_applicable(cart, coupon)
    
    def calculate_discount(self, cart: Cart, coupon: Coupon) -> float:
        """Calculate discount amount"""
        if coupon.type not in self.strategies:
            raise UnsupportedCouponTypeError(f"Unsupported coupon type: {coupon.type}")
        
        strategy = self.strategies[coupon.type]
        return strategy.calculate_discount(cart, coupon)
    
    def apply_discount(self, cart: Cart, coupon: Coupon):
        """Apply discount to cart"""
        if coupon.type not in self.strategies:
            raise UnsupportedCouponTypeError(f"Unsupported coupon type: {coupon.type}")
        
        strategy = self.strategies[coupon.type]
        return strategy.apply_discount(cart, coupon)