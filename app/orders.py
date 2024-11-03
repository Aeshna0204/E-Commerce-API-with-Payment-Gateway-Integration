from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas , models
from app.schemas import UserResponse, ProductResponse, OrderResponse, OrderUpdate, OrderCreate,OrderItem,OrderItemResponse
from app.models import User, Product, Order,OrderItem
from app.database import get_db  # Assuming get_db is defined to provide a DB session
from app.dependencies import get_current_user, require_admin, require_user  # Dependency to get the logged-in user

router = APIRouter()

# Endpoint to create a new order (User-only)
@router.post("/orders/", response_model=OrderResponse)
def place_order(order: OrderCreate, db: Session = Depends(get_db), user: User = Depends(require_user)):
    # Create the order record
    db_order = Order(user_id=user.id, status="pending")
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    order_items_response = []
    
    # Process each item and create an entry in OrderItem
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or product.stock < item.quantity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or insufficient stock")

        # Deduct stock, add OrderItem entry
        product.stock -= item.quantity
        db_order_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )
        db.add(db_order_item)
        db.commit()
        db.refresh(db_order_item)
        
        # Append to response
        order_items_response.append(OrderItemResponse(
            product_id=item.product_id,
            product_name=product.name,
            quantity=item.quantity,
            price=product.price
        ))

    # Construct final response
    return OrderResponse(
        id=db_order.id,
        user_id=db_order.user_id,
        items=order_items_response,
        status=db_order.status
    )



# Endpoint to view all orders (Admin-only)
@router.get("/orders/", response_model=List[OrderResponse])
def view_all_orders(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(Order).all()

# Endpoint for a user to view their own orders
@router.get("/orders/my-orders", response_model=List[OrderResponse])
def view_user_orders(db: Session = Depends(get_db), user: User = Depends(require_user)):
    # Fetch orders for the user
    orders = db.query(Order).filter(Order.user_id == user.id).all()

    # Populate product_name for each order item
    for order in orders:
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            item.product_name = product.name if product else "Unknown Product"

    return orders

