from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.post("/add", response_model=schemas.CartItemResponse)
def add_to_cart(
    cart_item: schemas.CartItemCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    item = db.query(models.Item).filter(models.Item.id == cart_item.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    existing_cart_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.item_id == cart_item.item_id
    ).first()
    
    if existing_cart_item:
        existing_cart_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_cart_item)
        return existing_cart_item
    
    new_cart_item = models.CartItem(
        user_id=user_id,
        item_id=cart_item.item_id,
        quantity=cart_item.quantity
    )
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return new_cart_item

@router.get("/{user_id}", response_model=list[schemas.CartItemResponse])
def get_cart(user_id: str, db: Session = Depends(get_db)):
    cart_items = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id
    ).all()
    return cart_items

@router.delete("/{user_id}/item/{item_id}")
def remove_from_cart(user_id: str, item_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.item_id == item_id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}

@router.delete("/{user_id}/clear")
def clear_cart(user_id: str, db: Session = Depends(get_db)):
    db.query(models.CartItem).filter(models.CartItem.user_id == user_id).delete()
    db.commit()
    return {"message": "Cart cleared"}

