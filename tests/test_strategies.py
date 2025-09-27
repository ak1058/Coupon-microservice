# tests/test_strategies.py
import pytest
from app.strategies import CartWiseStrategy, ProductWiseStrategy, BxGyStrategy
from app.schemas.cart import Cart, CartItem
from app.models.coupon import Coupon

class TestCartWiseStrategy:
    def test_cart_wise_applicable_above_threshold(self):
        strategy = CartWiseStrategy()
        cart = Cart(items=[
            CartItem(product_id=1, quantity=2, price=60.0)  # Total: 120
        ])
        coupon = Coupon(
            type="cart-wise",
            details={"threshold": 100, "discount": 10, "discount_type": "percentage"}
        )
        
        assert strategy.is_applicable(cart, coupon) == True
    
    def test_cart_wise_not_applicable_below_threshold(self):
        strategy = CartWiseStrategy()
        cart = Cart(items=[
            CartItem(product_id=1, quantity=1, price=50.0)  # Total: 50
        ])
        coupon = Coupon(
            type="cart-wise",
            details={"threshold": 100, "discount": 10, "discount_type": "percentage"}
        )
        
        assert strategy.is_applicable(cart, coupon) == False
    
    def test_cart_wise_calculate_percentage_discount(self):
        strategy = CartWiseStrategy()
        cart = Cart(items=[
            CartItem(product_id=1, quantity=2, price=50.0)  # Total: 100
        ])
        coupon = Coupon(
            type="cart-wise",
            details={"threshold": 50, "discount": 10, "discount_type": "percentage"}
        )
        
        discount = strategy.calculate_discount(cart, coupon)
        assert discount == 10.0  # 10% of 100
    
    def test_cart_wise_calculate_fixed_discount(self):
        strategy = CartWiseStrategy()
        cart = Cart(items=[
            CartItem(product_id=1, quantity=2, price=50.0)  # Total: 100
        ])
        coupon = Coupon(
            type="cart-wise",
            details={"threshold": 50, "discount": 15, "discount_type": "fixed"}
        )
        
        discount = strategy.calculate_discount(cart, coupon)
        assert discount == 15.0

class TestProductWiseStrategy:
    def test_product_wise_applicable_with_target_product(self):
        strategy = ProductWiseStrategy()
        cart = Cart(items=[
            CartItem(product_id=1, quantity=2, price=50.0),
            CartItem(product_id=2, quantity=1, price=30.0)
        ])
        coupon = Coupon(
            type="product-wise",
            details={"product_id": 1, "discount": 20, "discount_type": "percentage", "quantity_threshold": 1}
        )
        
        assert strategy.is_applicable(cart, coupon) == True
    
    def test_product_wise_not_applicable_without_target_product(self):
        strategy = ProductWiseStrategy()
        cart = Cart(items=[
            CartItem(product_id=2, quantity=1, price=30.0)
        ])
        coupon = Coupon(
            type="product-wise",
            details={"product_id": 1, "discount": 20, "discount_type": "percentage"}
        )
        
        assert strategy.is_applicable(cart, coupon) == False
    
    def test_product_wise_calculate_discount(self):
        strategy = ProductWiseStrategy()
        cart = Cart(items=[
            CartItem(product_id=1, quantity=2, price=50.0),  # Total for product 1: 100
            CartItem(product_id=2, quantity=1, price=30.0)
        ])
        coupon = Coupon(
            type="product-wise",
            details={"product_id": 1, "discount": 20, "discount_type": "percentage"}
        )
        
        discount = strategy.calculate_discount(cart, coupon)
        assert discount == 20.0  # 20% of 100

class TestBxGyStrategy:
    def test_bxgy_applicable_with_sufficient_products(self):
        strategy = BxGyStrategy()
        cart = Cart(items=[
            CartItem(product_id=1, quantity=3, price=50.0),  # Buy product
            CartItem(product_id=2, quantity=1, price=25.0)   # Get product
        ])
        coupon = Coupon(
            type="bxgy",
            details={
                "buy_products": [{"product_id": 1, "quantity": 2}],
                "get_products": [{"product_id": 2, "quantity": 1}],
                "repetition_limit": 1
            }
        )
        
        assert strategy.is_applicable(cart, coupon) == True
    
    def test_bxgy_not_applicable_insufficient_buy_products(self):
        strategy = BxGyStrategy()
        cart = Cart(items=[
            CartItem(product_id=1, quantity=1, price=50.0),  # Insufficient buy products
            CartItem(product_id=2, quantity=1, price=25.0)
        ])
        coupon = Coupon(
            type="bxgy",
            details={
                "buy_products": [{"product_id": 1, "quantity": 2}],
                "get_products": [{"product_id": 2, "quantity": 1}],
                "repetition_limit": 1
            }
        )
        
        assert strategy.is_applicable(cart, coupon) == False
    
    def test_bxgy_calculate_discount_with_repetition(self):
        strategy = BxGyStrategy()
        cart = Cart(items=[
            CartItem(product_id=1, quantity=6, price=50.0),  # Can form 3 buy sets
            CartItem(product_id=2, quantity=2, price=25.0)   # 2 get products available
        ])
        coupon = Coupon(
            type="bxgy",
            details={
                "buy_products": [{"product_id": 1, "quantity": 2}],
                "get_products": [{"product_id": 2, "quantity": 1}],
                "repetition_limit": 3
            }
        )
        
        discount = strategy.calculate_discount(cart, coupon)
        assert discount == 50.0  # 2 products * 25 each = 50