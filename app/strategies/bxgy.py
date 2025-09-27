# app/strategies/bxgy.py
from .base import DiscountStrategy
from ..schemas.cart import Cart, UpdatedCart, CartItemResponse
from ..models.coupon import Coupon
from collections import defaultdict

class BxGyStrategy(DiscountStrategy):
    """Strategy for Buy X Get Y discount coupons"""
    
    def is_applicable(self, cart: Cart, coupon: Coupon) -> bool:
        details = coupon.details
        buy_products = details.get('buy_products', [])
        get_products = details.get('get_products', [])
        
        # Check if we have enough buy products
        cart_quantities = {item.product_id: item.quantity for item in cart.items}
        
        # Calculate how many "buy" sets we can form
        buy_sets_possible = self._calculate_buy_sets(cart_quantities, buy_products)
        
        # Check if we have at least one get product
        has_get_products = any(
            cart_quantities.get(get_prod.get('product_id', 0), 0) > 0 
            for get_prod in get_products
        )
        
        return buy_sets_possible > 0 and has_get_products
    
    def _calculate_buy_sets(self, cart_quantities: dict, buy_products: list) -> int:
        """Calculate how many complete 'buy' sets we can form"""
        if not buy_products:
            return 0
            
        min_sets = float('inf')
        for buy_prod in buy_products:
            product_id = buy_prod.get('product_id', 0)
            required_quantity = buy_prod.get('quantity', 1)
            available_quantity = cart_quantities.get(product_id, 0)
            
            if available_quantity < required_quantity:
                return 0  # Cannot form even one set
            
            sets_from_this_product = available_quantity // required_quantity
            min_sets = min(min_sets, sets_from_this_product)
        
        return min_sets if min_sets != float('inf') else 0
    
    def calculate_discount(self, cart: Cart, coupon: Coupon) -> float:
        if not self.is_applicable(cart, coupon):
            return 0.0
            
        details = coupon.details
        buy_products = details.get('buy_products', [])
        get_products = details.get('get_products', [])
        repetition_limit = details.get('repetition_limit', 1)
        
        cart_quantities = {item.product_id: item.quantity for item in cart.items}
        cart_prices = {item.product_id: item.price for item in cart.items}
        
        # Calculate buy sets possible
        buy_sets_possible = self._calculate_buy_sets(cart_quantities, buy_products)
        
        # Apply repetition limit
        actual_applications = min(buy_sets_possible, repetition_limit)
        
        # Calculate total discount from free products
        total_discount = 0.0
        for get_prod in get_products:
            product_id = get_prod.get('product_id', 0)
            free_quantity_per_application = get_prod.get('quantity', 1)
            
            if product_id in cart_quantities and product_id in cart_prices:
                total_free_quantity = min(
                    actual_applications * free_quantity_per_application,
                    cart_quantities[product_id]
                )
                total_discount += total_free_quantity * cart_prices[product_id]
        
        return total_discount
    
    def apply_discount(self, cart: Cart, coupon: Coupon) -> UpdatedCart:
        details = coupon.details
        buy_products = details.get('buy_products', [])
        get_products = details.get('get_products', [])
        repetition_limit = details.get('repetition_limit', 1)
        
        cart_total = self._calculate_cart_total(cart)
        cart_quantities = {item.product_id: item.quantity for item in cart.items}
        cart_prices = {item.product_id: item.price for item in cart.items}
        
        # Calculate applications
        buy_sets_possible = self._calculate_buy_sets(cart_quantities, buy_products)
        actual_applications = min(buy_sets_possible, repetition_limit)
        
        # Calculate free quantities for each product
        free_quantities = defaultdict(int)
        total_discount = 0.0
        
        for get_prod in get_products:
            product_id = get_prod.get('product_id', 0)
            free_quantity_per_application = get_prod.get('quantity', 1)
            
            if product_id in cart_quantities:
                total_free_quantity = min(
                    actual_applications * free_quantity_per_application,
                    cart_quantities[product_id]
                )
                free_quantities[product_id] = total_free_quantity
                if product_id in cart_prices:
                    total_discount += total_free_quantity * cart_prices[product_id]
        
        # Build response items
        items_response = []
        for item in cart.items:
            item_discount = 0.0
            if item.product_id in free_quantities:
                free_qty = free_quantities[item.product_id]
                item_discount = free_qty * item.price
            
            items_response.append(CartItemResponse(
                product_id=item.product_id,
                quantity=item.quantity + free_quantities.get(item.product_id, 0),  # Add free items
                price=item.price,
                total_discount=round(item_discount, 2),
                discounted_price=item.price if item_discount == 0 else 0  # Free items are $0
            ))
        
        return UpdatedCart(
            items=items_response,
            total_price=cart_total,
            total_discount=round(total_discount, 2),
            final_price=round(cart_total - total_discount, 2)
        )
