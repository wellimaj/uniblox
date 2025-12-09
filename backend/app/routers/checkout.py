from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models, schemas

router = APIRouter()

NTH_ORDER = 5

@router.post("/", response_model=schemas.CheckoutResponse)
def checkout(
    checkout_request: schemas.CheckoutRequest,
    db: Session = Depends(get_db)
):
    cart_items = db.query(models.CartItem).filter(
        models.CartItem.user_id == checkout_request.user_id
    ).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total_amount = sum(item.item.price * item.quantity for item in cart_items)
    discount_amount = 0.0
    discount_code_used = None
    
    if checkout_request.discount_code:
        discount = db.query(models.DiscountCode).filter(
            models.DiscountCode.code == checkout_request.discount_code,
            models.DiscountCode.is_used == False
        ).first()
        
        if not discount:
            raise HTTPException(status_code=400, detail="Invalid or already used discount code")
        
        discount_amount = total_amount * (discount.discount_percentage / 100)
        discount_code_used = discount.code
        discount.is_used = True
    
    final_amount = total_amount - discount_amount
    
    order_count_before = db.query(func.count(models.Order.id)).scalar()
    
    order = models.Order(
        user_id=checkout_request.user_id,
        total_amount=total_amount,
        discount_amount=discount_amount,
        discount_code=discount_code_used
    )
    db.add(order)
    db.flush()
    
    for cart_item in cart_items:
        order_item = models.OrderItem(
            order_id=order.id,
            item_id=cart_item.item_id,
            quantity=cart_item.quantity,
            price=cart_item.item.price
        )
        db.add(order_item)
    
    db.query(models.CartItem).filter(
        models.CartItem.user_id == checkout_request.user_id
    ).delete()
    
    if (order_count_before + 1) % NTH_ORDER == 0:
        new_discount_code = models.DiscountCode(
            code=f"SAVE10_{order.id}",
            discount_percentage=10.0,
            order_id=order.id
        )
        db.add(new_discount_code)
    
    db.commit()
    db.refresh(order)
    
    return schemas.CheckoutResponse(
        order_id=order.id,
        total_amount=total_amount,
        discount_amount=discount_amount,
        final_amount=final_amount,
        discount_code=discount_code_used
    )

