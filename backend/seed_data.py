from app.database import SessionLocal, engine, Base
from app import models
import time

def seed_data():
    Base.metadata.create_all(bind=engine)
    time.sleep(1)
    
    db = SessionLocal()
    try:
        items = [
            models.Item(name="Laptop", price=999.99, description="High-performance laptop"),
            models.Item(name="Mouse", price=29.99, description="Wireless mouse"),
            models.Item(name="Keyboard", price=79.99, description="Mechanical keyboard"),
            models.Item(name="Monitor", price=299.99, description="27-inch 4K monitor"),
            models.Item(name="Headphones", price=149.99, description="Noise-cancelling headphones"),
        ]
        
        for item in items:
            existing = db.query(models.Item).filter(models.Item.name == item.name).first()
            if not existing:
                db.add(item)
        
        db.commit()
        print("Seed data created successfully!")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()

