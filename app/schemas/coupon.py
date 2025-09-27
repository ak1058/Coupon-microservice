# app/schemas/coupon.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class CouponType(str, Enum):
    CART_WISE = "cart-wise"
    PRODUCT_WISE = "product-wise"
    BXGY = "bxgy"

# Base schemas for different coupon types
class CartWiseDetails(BaseModel):
    threshold: float = Field(..., gt=0, description="Minimum cart value to apply discount")
    discount: Union[float, int] = Field(..., gt=0, description="Discount percentage or amount")
    discount_type: str = Field(default="percentage", description="'percentage' or 'fixed'")

class ProductWiseDetails(BaseModel):
    product_id: int = Field(..., description="Product ID to apply discount on")
    discount: Union[float, int] = Field(..., gt=0)
    discount_type: str = Field(default="percentage")
    quantity_threshold: Optional[int] = Field(default=1, description="Minimum quantity required")

class BxGyProduct(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class BxGyDetails(BaseModel):
    buy_products: List[BxGyProduct] = Field(..., min_items=1)
    get_products: List[BxGyProduct] = Field(..., min_items=1)
    repetition_limit: int = Field(default=1, gt=0)

# Request schemas
class CouponCreateRequest(BaseModel):
    type: CouponType
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    details: Union[CartWiseDetails, ProductWiseDetails, BxGyDetails]
    expires_at: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, gt=0)
    
    @validator('details', pre=True)
    def validate_details(cls, v, values):
        coupon_type = values.get('type')
        if coupon_type == CouponType.CART_WISE:
            return CartWiseDetails(**v)
        elif coupon_type == CouponType.PRODUCT_WISE:
            return ProductWiseDetails(**v)
        elif coupon_type == CouponType.BXGY:
            return BxGyDetails(**v)
        return v

class CouponUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    details: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

# Response schemas
class CouponResponse(BaseModel):
    id: str
    type: str
    title: str
    description: Optional[str]
    details: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    usage_limit: Optional[int]
    usage_count: int
    
    class Config:
        from_attributes = True