# Coupon Microservice

## 📂 Project Structure
```
app/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration management
├── database.py             # Database connection and session
├── models/                 # SQLAlchemy models
├── schemas/                # Pydantic schemas for validation
├── services/               # Business logic layer
├── strategies/             # Strategy pattern implementations
├── repositories/           # Data access layer
├── api/routes/             # API route handlers
└── exceptions/             # Custom exception classes
```

## 🔗 API Endpoints

### Coupon Management
- **POST** `/coupons` - Create a new coupon  
- **GET** `/coupons` - Retrieve all active coupons  
- **GET** `/coupons/{id}` - Retrieve specific coupon by ID  
- **PUT** `/coupons/{id}` - Update specific coupon by ID  
- **DELETE** `/coupons/{id}` - Delete (soft delete) coupon by ID  

### Coupon Application
- **POST** `/coupons/applicable-coupons` - Get all applicable coupons for a cart  
- **POST** `/coupons/apply-coupon/{id}` - Apply specific coupon to cart  

### Utility
- **GET** `/health` - Health check endpoint  
- **GET** `/` - API information  

---

## 🏷️ Coupon Types

### 1. Cart-wise Coupons
Apply discounts to the entire cart based on cart total threshold.

Example:
```json
{
  "type": "cart-wise",
  "title": "10% Off on Orders Above Rs.100",
  "description": "Get 10% discount up to maximum ₹500 off on orders above ₹2000",
  "details": {
    "threshold": 100.0,
    "discount": 10,
    "discount_type": "percentage"
  },
  "expires_at": "2024-12-31T23:59:59",
  "usage_limit": 1000
}
```

### 2. Product-wise Coupons
Apply discounts to specific products in the cart.

Example:
```json
{
  "type": "product-wise",
  "title": "20% Off Product A",
  "details": {
    "product_id": 1,
    "discount": 20,
    "discount_type": "percentage",
    "quantity_threshold": 2
  }
}
```

### 3. Buy X Get Y (BxGy) Coupons
Buy specified products and get other products for free with repetition limits.

Example:
```json
{
  "type": "bxgy",
  "title": "Buy 2 Get 1 Free",
  "details": {
    "buy_products": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 2}
    ],
    "get_products": [
      {"product_id": 3, "quantity": 1}
    ],
    "repetition_limit": 3
  }
}
```

---

## ✅ Implemented Cases

### Cart-wise Coupons
- Percentage discount on cart total
  - 10% off on carts over Rs.100
  - 15% off on carts over Rs.200
- Fixed amount discount on cart total
  - Rs.10 off on carts over Rs.50
  - Rs.25 off on carts over Rs.150
- Conditional coupons with discount cap
  - 10% off up to Rs.500 over transactions greater than Rs.2000
- Proportional distribution of cart discount
  - Discount distributed proportionally across all cart items

### Product-wise Coupons
- Percentage discount on specific products
  - 20% off on Product A
  - 30% off on Product B when quantity ≥ 3
- Fixed amount discount per product
  - $5 off per unit of Product C
  - $10 off per unit of Product D
- Quantity threshold requirements
  - Discount applies only when minimum quantity is met

### BxGy Coupons
- Simple Buy X Get Y
  - Buy 2 of Product A, get 1 of Product B free
  - Buy 3 of any product from [X, Y, Z], get 1 from [A, B] free
- Multi-product buy conditions
  - Buy 2 from [Product 1, Product 2] and get 1 from [Product 3, Product 4] free
- Repetition limits
  - Apply coupon maximum 3 times
  - Handle cases where buy products exceed repetition capacity
- Complex scenarios
  - Buy 6 products from buy array, get 3 products free (with repetition limit 3)
  - Partial fulfillment when get products are limited

---

##  Cases Considered But Not Fully Implemented

### Advanced Cart-wise Cases
- Category-based cart discounts
- Time-based discounts (happy hour, day-of-week)
- User-specific cart discounts (first-time buyer, loyalty tier)
 **Reason for not implementing now**: Would require a Product Catalog Service with category information, scheduling/cron job system (for time based cupons), require user info(for user specific discounts)

### Advanced Product-wise Cases
- Cross-product dependencies
- Bundle discounts
- Tiered discounts by quantity
- Brand/Category specific discounts
 **Reason for not implementing now**: requires more strategy pattern enhancement requuires time but can be implemented

### Advanced BxGy Cases
- Weighted BxGy (based on cart value)
- Cross-category BxGy (electronics + accessories, clothing + free shipping)
- Progressive BxGy (increasing benefits with repetition)
**Reason for not implementing now**: requires advanced cart analysis algorithms

### Complex Combination Cases
- Stackable coupons (multiple coupons applied)
- Priority-based coupon application
- Exclusion rules (categories/products excluded)
- Min/Max discount limits

---

##  Assumptions

### General Assumptions
- Product IDs are unique positive integers
- Prices are positive numbers
- Quantities are positive integers
- Single currency (no conversion)

### Cart Assumptions
- Cart items are independent unless specified in coupon rules
- Cart state is stateless per API call
- No user context considered

### Coupon Assumptions
- Coupon details immutable during application
- All timestamps in UTC
- Soft delete approach for coupons
- Usage tracking assumed accurate

### BxGy Specific Assumptions
- Buy products can also be get products
- Repetition limited by buy capacity & get availability
- Free products increase cart quantity
- Free products shown with $Rs. 0 price
