# app/api/routes/coupons.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...database import get_db
from ...schemas.coupon import CouponCreateRequest, CouponUpdateRequest, CouponResponse
from ...schemas.cart import (
    ApplyCouponRequest, 
    ApplyCouponResponse, 
    ApplicableCouponsResponse,
    Cart
)
from ...services.coupon_service import CouponService
from ...exceptions.custom_exceptions import (
    CouponNotFoundError,
    CouponExpiredError,
    CouponUsageLimitExceededError,
    CouponNotApplicableError,
    UnsupportedCouponTypeError,
    InvalidCartError
)

router = APIRouter(prefix="/coupons", tags=["coupons"])

def get_coupon_service(db: Session = Depends(get_db)) -> CouponService:
    """Dependency to get coupon service"""
    return CouponService(db)

@router.post("/", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    coupon_data: CouponCreateRequest,
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """
    Create a new coupon
    
    - **type**: Type of coupon (cart-wise, product-wise, bxgy)
    - **title**: Coupon title
    - **description**: Optional description
    - **details**: Type-specific coupon details
    - **expires_at**: Optional expiration date
    - **usage_limit**: Optional usage limit
    """
    try:
        return coupon_service.create_coupon(coupon_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating coupon: {str(e)}"
        )

@router.get("/", response_model=List[CouponResponse])
async def get_all_coupons(
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """
    Retrieve all active coupons
    """
    return coupon_service.get_all_coupons()

@router.get("/{coupon_id}", response_model=CouponResponse)
async def get_coupon(
    coupon_id: str,
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """
    Retrieve a specific coupon by ID
    """
    try:
        return coupon_service.get_coupon(coupon_id)
    except CouponNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{coupon_id}", response_model=CouponResponse)
async def update_coupon(
    coupon_id: str,
    update_data: CouponUpdateRequest,
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """
    Update a specific coupon by ID
    """
    try:
        return coupon_service.update_coupon(coupon_id, update_data)
    except CouponNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating coupon: {str(e)}"
        )

@router.delete("/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(
    coupon_id: str,
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """
    Delete a specific coupon by ID (soft delete)
    """
    try:
        coupon_service.delete_coupon(coupon_id)
    except CouponNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/applicable-coupons", response_model=ApplicableCouponsResponse)
async def get_applicable_coupons(
    request: ApplyCouponRequest,
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """
    Fetch all applicable coupons for a given cart and calculate discounts
    
    Request body should contain:
    - **cart**: Cart with items (product_id, quantity, price)
    """
    try:
        applicable_coupons = coupon_service.get_applicable_coupons(request.cart)
        return ApplicableCouponsResponse(applicable_coupons=applicable_coupons)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching applicable coupons: {str(e)}"
        )

@router.post("/apply-coupon/{coupon_id}", response_model=ApplyCouponResponse)
async def apply_coupon(
    coupon_id: str,
    request: ApplyCouponRequest,
    coupon_service: CouponService = Depends(get_coupon_service)
):
    """
    Apply a specific coupon to the cart and return updated cart with discounts
    
    Request body should contain:
    - **cart**: Cart with items (product_id, quantity, price)
    """
    try:
        updated_cart = coupon_service.apply_coupon(coupon_id, request.cart)
        return ApplyCouponResponse(updated_cart=updated_cart)
    except CouponNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (CouponExpiredError, CouponUsageLimitExceededError, CouponNotApplicableError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except UnsupportedCouponTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error applying coupon: {str(e)}"
        )