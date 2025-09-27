# tests/test_coupons.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from datetime import datetime, timedelta

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

class TestCouponEndpoints:
    def test_create_cart_wise_coupon(self):
        coupon_data = {
            "type": "cart-wise",
            "title": "10% Off Cart",
            "description": "Get 10% off on orders above $100",
            "details": {
                "threshold": 100.0,
                "discount": 10,
                "discount_type": "percentage"
            }
        }
        
        response = client.post("/coupons/", json=coupon_data)
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "cart-wise"
        assert data["title"] == "10% Off Cart"
    
    def test_create_product_wise_coupon(self):
        coupon_data = {
            "type": "product-wise",
            "title": "20% Off Product 1",
            "details": {
                "product_id": 1,
                "discount": 20,
                "discount_type": "percentage"
            }
        }
        
        response = client.post("/coupons/", json=coupon_data)
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "product-wise"
    
    def test_create_bxgy_coupon(self):
        coupon_data = {
            "type": "bxgy",
            "title": "Buy 2 Get 1 Free",
            "details": {
                "buy_products": [{"product_id": 1, "quantity": 2}],
                "get_products": [{"product_id": 3, "quantity": 1}],
                "repetition_limit": 2
            }
        }
        
        response = client.post("/coupons/", json=coupon_data)
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "bxgy"
    
    def test_get_all_coupons(self):
        response = client.get("/coupons/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_applicable_coupons(self):
        # First create a coupon
        coupon_data = {
            "type": "cart-wise",
            "title": "Test Coupon",
            "details": {
                "threshold": 100.0,
                "discount": 10,
                "discount_type": "percentage"
            }
        }
        client.post("/coupons/", json=coupon_data)
        
        # Test applicable coupons
        cart_data = {
            "cart": {
                "items": [
                    {"product_id": 1, "quantity": 2, "price": 60.0}
                ]
            }
        }
        
        response = client.post("/coupons/applicable-coupons", json=cart_data)
        assert response.status_code == 200
        data = response.json()
        assert "applicable_coupons" in data
    
    def test_apply_coupon(self):
        # Create a coupon first
        coupon_data = {
            "type": "cart-wise",
            "title": "Apply Test Coupon",
            "details": {
                "threshold": 50.0,
                "discount": 10,
                "discount_type": "percentage"
            }
        }
        create_response = client.post("/coupons/", json=coupon_data)
        coupon_id = create_response.json()["id"]
        
        # Apply the coupon
        cart_data = {
            "cart": {
                "items": [
                    {"product_id": 1, "quantity": 2, "price": 50.0}
                ]
            }
        }
        
        response = client.post(f"/coupons/apply-coupon/{coupon_id}", json=cart_data)
        assert response.status_code == 200
        data = response.json()
        assert "updated_cart" in data
        assert data["updated_cart"]["total_discount"] > 0

if __name__ == "__main__":
    pytest.main([__file__])