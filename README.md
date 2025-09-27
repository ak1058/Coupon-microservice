# Coupon Microservice

A RESTful API to manage and apply different types of discount coupons (cart-wise, product-wise, and BxGy) for an e-commerce platform, designed for extensibility and performance.

## 🚀 Features

- **Multiple Coupon Types**: Cart-wise, Product-wise, Buy X Get Y (BxGy)
- **Extensible Architecture**: Strategy pattern for easy addition of new coupon types
- **Advanced Logic**: Handles complex scenarios including repetition limits, thresholds, and multiple products
- **Performance Optimized**: Efficient discount calculations and database operations
- **Comprehensive Testing**: Unit tests for all major components
- **Error Handling**: Detailed validation and error responses
- **Database Agnostic**: Uses SQLAlchemy ORM (currently configured for PostgreSQL)

## 🏗️ Architecture

### Core Components

- **Coupon Strategies**: Implemented using Strategy pattern for different coupon types
- **RESTful API**: FastAPI-based endpoints for coupon management and application
- **Database Models**: SQLAlchemy models for coupons, products, and discount applications
- **Validation**: Pydantic models for request/response validation

### Coupon Types Supported

1. **Cart-wise Discounts**: Percentage or fixed amount discounts on entire cart
2. **Product-wise Discounts**: Discounts applied to specific products
3. **Buy X Get Y (BxGy)**: Buy X items, get Y items free or discounted


## Setup Instructions

You can set up this project in **two ways**: either using **Docker** or the **normal way**.

```bash
# Clone the repository
git clone https://github.com/ak1058/Coupon-microservice.git
cd coupon-microservice
```
---

### Environment Variables

Update your `.env` file with the following variables (change values according to your setup):

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=coupon_microservice_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

---

## Option 1: Using Docker

1. Run the following command:

   ```bash
   docker-compose up --build
   ```

2. Access the application at: [http://localhost:8000](http://localhost:8000)  
3. API Docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Option 2: Normal Setup (without Docker)

1. Ensure you have **Python 3.11** installed (if not, use Docker).  
2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - On **MacOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the server:

   ```bash
   uvicorn app.main:app --reload
   ```

---

## Running Tests

This project includes **16 tests** in total:

- **6 tests in `test_coupons.py`**:
  - `test_create_cart_wise_coupon`
  - `test_create_product_wise_coupon`
  - `test_create_bxgy_coupon`
  - `test_get_all_coupons`
  - `test_applicable_coupons`
  - `test_apply_coupon`

- **10 tests in `test_strategies.py`**:
  - `test_cart_wise_applicable_above_threshold`
  - `test_cart_wise_not_applicable_below_threshold`
  - `test_cart_wise_calculate_percentage_discount`
  - `test_cart_wise_calculate_fixed_discount`
  - `test_product_wise_applicable_with_target_product`
  - `test_product_wise_not_applicable_without_target_product`
  - `test_product_wise_calculate_discount`
  - `test_bxgy_applicable_with_sufficient_products`
  - `test_bxgy_not_applicable_insufficient_buy_products`
  - `test_bxgy_calculate_discount_with_repetition`

Run the tests with:

```bash
pytest
```

---

## Documentation

For documented cases and limitations, please refer to **`document_readme.md`** (present in the same folder).
