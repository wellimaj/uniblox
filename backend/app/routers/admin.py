from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models, schemas

router = APIRouter()

NTH_ORDER = 5

@router.post("/discount/generate", response_model=schemas.DiscountCodeResponse)
def generate_discount_code(db: Session = Depends(get_db)):
    order_count = db.query(func.count(models.Order.id)).scalar()
    
    if order_count % NTH_ORDER != 0:
        raise HTTPException(
            status_code=400,
            detail=f"Discount code can only be generated every {NTH_ORDER} orders. Current order count: {order_count}"
        )
    
    existing_unused = db.query(models.DiscountCode).filter(
        models.DiscountCode.is_used == False
    ).first()
    
    if existing_unused:
        raise HTTPException(
            status_code=400,
            detail="A discount code is already available and unused. Use it before generating a new one."
        )
    
    last_order = db.query(models.Order).order_by(models.Order.id.desc()).first()
    if not last_order:
        raise HTTPException(status_code=400, detail="No orders found")
    
    new_discount_code = models.DiscountCode(
        code=f"SAVE10_{last_order.id}",
        discount_percentage=10.0,
        order_id=last_order.id
    )
    db.add(new_discount_code)
    db.commit()
    db.refresh(new_discount_code)
    
    return new_discount_code

@router.get("/discount/available", response_model=list[schemas.DiscountCodeResponse])
def get_available_discount_codes(db: Session = Depends(get_db)):
    available_codes = db.query(models.DiscountCode).filter(
        models.DiscountCode.is_used == False
    ).all()
    return available_codes

@router.get("/stats", response_model=schemas.AdminStatsResponse)
def get_admin_stats(db: Session = Depends(get_db)):
    total_items_purchased = db.query(
        func.sum(models.OrderItem.quantity)
    ).scalar() or 0
    
    total_purchase_amount = db.query(
        func.sum(models.Order.total_amount)
    ).scalar() or 0.0
    
    discount_codes = db.query(models.DiscountCode).all()
    
    total_discount_amount = db.query(
        func.sum(models.Order.discount_amount)
    ).scalar() or 0.0
    
    return schemas.AdminStatsResponse(
        total_items_purchased=int(total_items_purchased),
        total_purchase_amount=float(total_purchase_amount),
        discount_codes=discount_codes,
        total_discount_amount=float(total_discount_amount)
    )

