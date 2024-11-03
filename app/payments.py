from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from paypalrestsdk import Payment
from app.database import get_db
from app.schemas import OrderResponse, OrderCreate, PaymentResponse, OrderItemResponse
from app.models import User, Order, Product, OrderItem
from app.dependencies import get_current_user, require_user
import paypalrestsdk
import os
from app.config import PAYPAL_CLIENT_ID,PAYPAL_CLIENT_SECRET,PAYPAL_MODE

router = APIRouter()

# Configure PayPal
paypalrestsdk.configure({
    "mode": PAYPAL_MODE,  # Or "live" for production
    "client_id": PAYPAL_CLIENT_SECRET,
    "client_secret": PAYPAL_CLIENT_ID
})

@router.post("/create-payment/{order_id}", response_model=PaymentResponse)
def create_payment(order_id: int, db: Session = Depends(get_db), user: User = Depends(require_user)):
    # Retrieve the order
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    print("order query"+str(order.id))
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Retrieve associated order items
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    print("order items"+str(order_items))
    if not order_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items found for this order")

    # Calculate the total amount
    total_amount = sum(item.product.price * item.quantity for item in order_items)
    print("total_amount_calculatedd"+ str(total_amount))

    # Create a PayPal payment
    payment = Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "transactions": [{
            "amount": {"total": f"{total_amount:.2f}", "currency": "USD"},
            "description": f"Payment for Order {order.id}"
        }],
        "redirect_urls": {
            "return_url": f"http://localhost:8000/payments/execute-payment/{order.id}",
            "cancel_url": "http://localhost:8000/payments/cancel"
        }
    })

    if payment.create():
        # Store the payment ID with the order in your database
        order.payment_id = payment.id  # Ensure you have a payment_id field in your Order model
        db.commit()
        # Return the PayPal approval URL to the frontend
        approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
        return {"payment_id": payment.id, "approval_url": approval_url}
    else:
        # Log the error response from PayPal for debugging
        print(payment.error)  # Log the error for debugging
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Payment creation failed")

@router.get("/execute-payment/{order_id}", response_model=OrderResponse)
def execute_payment(order_id: int, payer_id: str, payment_id: str, db: Session = Depends(get_db), user: User = Depends(require_user)):
    # Retrieve the order
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order or order.payment_id != payment_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found or payment ID mismatch")

    # Get the PayPal payment
    payment = Payment.find(payment_id)

    # Execute the payment with the payer_id from PayPal's response
    if payment.execute({"payer_id": payer_id}):
        # Update order status to "paid"
        order.status = "paid"
        db.commit()
        # Prepare response including order items
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        order_items_response = [
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.product.price
            ) for item in order_items
        ]
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            items=order_items_response,
            status=order.status
        )
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Payment execution failed")

@router.get("/cancel", response_model=dict)
def cancel_payment():
    return {"detail": "Payment was canceled"}
