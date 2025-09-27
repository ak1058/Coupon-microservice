# app/strategies/product_wise.py
from .base import DiscountStrategy
from ..schemas.cart import Cart, UpdatedCart, CartItemResponse
from ..models.coupon import Coupon

class ProductWiseStrategy(DiscountStrategy):
    """Strategy for product-wise discount coupons"""
    
    def is_applicable(self, cart: Cart, coupon: Coupon) -> bool:
        details = coupon.details
        target_product_id = details.get('product_id')
        quantity_threshold = details.get('quantity_threshold', 1)
        
        for item in cart.items:
            if item.product_id == target_product_id and item.quantity >= quantity_threshold:
                return True
        return False
    
    def calculate_discount(self, cart: Cart, coupon: Coupon) -> float:
        if not self.is_applicable(cart, coupon):
            return 0.0
            
        details = coupon.details
        target_product_id = details.get('product_id')
        discount = details.get('discount', 0)
        discount_type = details.get('discount_type', 'percentage')
        
        total_discount = 0.0
        for item in cart.items:
            if item.product_id == target_product_id:
                item_total = item.quantity * item.price
                if discount_type == 'percentage':
                    total_discount += (item_total * discount) / 100
                else:  # fixed amount per item
                    total_discount += min(discount * item.quantity, item_total)
        
        return total_discount
    
    def apply_discount(self, cart: Cart, coupon: Coupon) -> UpdatedCart:
        details = coupon.details
        target_product_id = details.get('product_id')
        discount = details.get('discount', 0)
        discount_type = details.get('discount_type', 'percentage')
        
        cart_total = self._calculate_cart_total(cart)
        total_discount = 0.0
        items_response = []
        
        for item in cart.items:
            item_discount = 0.0
            if item.product_id == target_product_id:
                item_total = item.quantity * item.price
                if discount_type == 'percentage':
                    item_discount = (item_total * discount) / 100
                else:  # fixed amount
                    item_discount = min(discount * item.quantity, item_total)
                total_discount += item_discount
            
            items_response.append(CartItemResponse(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                total_discount=round(item_discount, 2),
                discounted_price=item.price - (item_discount / item.quantity) if item.quantity > 0 and item_discount > 0 else item.price
            ))
        
        return UpdatedCart(
            items=items_response,
            total_price=cart_total,
            total_discount=round(total_discount, 2),
            final_price=round(cart_total - total_discount, 2)
        )