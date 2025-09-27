# app/schemas/cart.py
from pydantic import BaseModel, Field
from typing import List, Optional

class CartItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

class Cart(BaseModel):
    items: List[CartItem] = Field(..., min_items=1)

class CartItemResponse(BaseModel):
    product_id: int
    quantity: int
    price: float
    total_discount: float = 0.0
    discounted_price: Optional[float] = None

class UpdatedCart(BaseModel):
    items: List[CartItemResponse]
    total_price: float
    total_discount: float
    final_price: float

class ApplicableCoupon(BaseModel):
    coupon_id: str
    type: str
    discount: float

class ApplicableCouponsResponse(BaseModel):
    applicable_coupons: List[ApplicableCoupon]

class ApplyCouponRequest(BaseModel):
    cart: Cart

class ApplyCouponResponse(BaseModel):
    updated_cart: UpdatedCart