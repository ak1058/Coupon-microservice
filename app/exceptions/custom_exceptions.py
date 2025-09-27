# app/exceptions/custom_exceptions.py
class CouponManagementError(Exception):
    """Base exception for coupon management system"""
    pass

class CouponNotFoundError(CouponManagementError):
    """Raised when coupon is not found"""
    pass

class CouponExpiredError(CouponManagementError):
    """Raised when coupon has expired"""
    pass

class CouponUsageLimitExceededError(CouponManagementError):
    """Raised when coupon usage limit is exceeded"""
    pass

class CouponNotApplicableError(CouponManagementError):
    """Raised when coupon is not applicable to cart"""
    pass

class UnsupportedCouponTypeError(CouponManagementError):
    """Raised when coupon type is not supported"""
    pass

class InvalidCartError(CouponManagementError):
    """Raised when cart data is invalid"""
    pass