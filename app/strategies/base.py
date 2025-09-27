# app/strategies/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from ..schemas.cart import Cart, UpdatedCart, CartItemResponse
from ..models.coupon import Coupon

class DiscountStrategy(ABC):
    """Base strategy for discount calculations"""
    
    @abstractmethod
    def is_applicable(self, cart: Cart, coupon: Coupon) -> bool:
        """Check if coupon is applicable to the cart"""
        pass
    
    @abstractmethod
    def calculate_discount(self, cart: Cart, coupon: Coupon) -> float:
        """Calculate discount amount"""
        pass
    
    @abstractmethod
    def apply_discount(self, cart: Cart, coupon: Coupon) -> UpdatedCart:
        """Apply discount to cart and return updated cart"""
        pass
    
    def _calculate_cart_total(self, cart: Cart) -> float:
        """Helper method to calculate cart total"""
        return sum(item.quantity * item.price for item in cart.items)