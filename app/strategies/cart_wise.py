# app/strategies/cart_wise.py
from .base import DiscountStrategy
from ..schemas.cart import Cart, UpdatedCart, CartItemResponse
from ..models.coupon import Coupon

class CartWiseStrategy(DiscountStrategy):
    """Strategy for cart-wise discount coupons"""
    
    def is_applicable(self, cart: Cart, coupon: Coupon) -> bool:
        details = coupon.details
        cart_total = self._calculate_cart_total(cart)
        return cart_total >= details.get('threshold', 0)
    
    def calculate_discount(self, cart: Cart, coupon: Coupon) -> float:
        if not self.is_applicable(cart, coupon):
            return 0.0
            
        details = coupon.details
        cart_total = self._calculate_cart_total(cart)
        discount = details.get('discount', 0)
        discount_type = details.get('discount_type', 'percentage')
        max_discount = details.get('max_discount') or details.get('discount_cap')  
        
        if discount_type == 'percentage':
            calculated_discount = (cart_total * discount) / 100
            
            # Apply discount cap if specified
            if max_discount is not None:
                calculated_discount = min(calculated_discount, max_discount)
                
            return calculated_discount
        else:  # fixed amount
            return min(discount, cart_total)  # Don't exceed cart total
    
    def apply_discount(self, cart: Cart, coupon: Coupon) -> UpdatedCart:
        total_discount = self.calculate_discount(cart, coupon)
        cart_total = self._calculate_cart_total(cart)
        
        # For cart-wise, distribute discount proportionally across items
        items_response = []
        remaining_discount = total_discount
        
        for item in cart.items:
            item_total = item.quantity * item.price
            item_discount_ratio = item_total / cart_total if cart_total > 0 else 0
            item_discount = total_discount * item_discount_ratio
            
            items_response.append(CartItemResponse(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                total_discount=round(item_discount, 2),
                discounted_price=item.price - (item_discount / item.quantity) if item.quantity > 0 else item.price
            ))
        
        return UpdatedCart(
            items=items_response,
            total_price=cart_total,
            total_discount=round(total_discount, 2),
            final_price=round(cart_total - total_discount, 2)
        )