# E-Commerce Api Development with Payment Integration

This is a FastAPI-based backend for a E-commerce Api developement and PayPal payment integration. The project uses PostgreSQL as the database and SQLAlchemy ORM for data management.

---

## Table of Contents

- [Project Setup](#project-setup)
- [API Endpoints](#api-endpoints)
- [Dependencies](#dependencies)

---

## Project Setup

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- `pip` for package installation

## API Endpoints
#### Create a virtual environment:
```
virtualenv env
```
#### Run the backend server
```
uvicorn app.main:app --reload
```
### API Documentations
To register a user - post request
```
http://localhost:8000/auth/register
```
The input should contain a json format of username , password and role

To login a user - post request
```
http://localhost:8000/auth/login
```
The input should contain url-encoded format paramters- username and password

For creating product - post request {admin acess only}
```
http://localhost:8000/products/products/
```
For updating product -put request
```
http://localhost:8000/products/products/{product_id}
```
For deleting products - delete request
```
http://localhost:8000/products/products/{product_id}
```
for getting all the products - get request
```
http://localhost:8000/products/products/
```
for getting products by id - get request
```
http://localhost:8000/products/products/{product_id}
```

For creating order - post request {user acess only}
```
http://localhost:8000/orders/orders/
```
for getting all the orders - get request
```
http://localhost:8000/orders/orders/
```
for getting orders by user - get request
```
http://localhost:8000/orders/orders/my-orders
```
For creating payment - user acess only
```
http://localhost:8000/payments/create-payment/{order_id}
```
For executing payment - user acess only
```
http://localhost:8000/payments/execute-payment/{order_id}
```
For canceling payment - user acess only
```
http://localhost:8000/payments/cancel
```
