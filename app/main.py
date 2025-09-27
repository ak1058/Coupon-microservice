# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from .database import create_tables
from .api import coupons_router
from .exceptions.custom_exceptions import CouponManagementError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Database tables created successfully")
    yield
    # Shutdown: cleanup if needed
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Coupon Management API",
    description="""
    A RESTful API to manage and apply different types of discount coupons 
    (cart-wise, product-wise, and BxGy) for an e-commerce platform.
    
    ## Features
    - **Extensible Design**: Easy to add new coupon types
    - **Multiple Coupon Types**: Cart-wise, Product-wise, Buy X Get Y
    - **Advanced Logic**: Handles complex scenarios and edge cases
    - **Performance Optimized**: Efficient discount calculations
    - **Error Handling**: Comprehensive validation and error responses
    """,
    version="1.0.0",
    contact={
        "name": "Coupon Management API",
        "email": "support@example.com",
    },
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(coupons_router)

# Global exception handler for custom exceptions
@app.exception_handler(CouponManagementError)
async def coupon_management_exception_handler(request: Request, exc: CouponManagementError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_type": exc.__class__.__name__}
    )

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Coupon Management API is running"}

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Coupon Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

