import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app import models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def setup_items():
    db = TestingSessionLocal()
    item1 = models.Item(name="Test Item 1", price=10.0, description="Test description")
    item2 = models.Item(name="Test Item 2", price=20.0, description="Test description")
    db.add(item1)
    db.add(item2)
    db.commit()
    db.refresh(item1)
    db.refresh(item2)
    db.close()
    return [item1.id, item2.id]

def test_checkout_without_discount(setup_items):
    item_id = setup_items[0]
    client.post(
        "/api/cart/add?user_id=test_user",
        json={"item_id": item_id, "quantity": 2}
    )
    response = client.post(
        "/api/checkout/",
        json={"user_id": "test_user", "discount_code": None}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_amount"] == 20.0
    assert data["discount_amount"] == 0.0
    assert data["final_amount"] == 20.0

def test_checkout_with_invalid_discount(setup_items):
    item_id = setup_items[0]
    client.post(
        "/api/cart/add?user_id=test_user",
        json={"item_id": item_id, "quantity": 1}
    )
    response = client.post(
        "/api/checkout/",
        json={"user_id": "test_user", "discount_code": "INVALID"}
    )
    assert response.status_code == 400

def test_checkout_with_valid_discount(setup_items):
    db = TestingSessionLocal()
    discount = models.DiscountCode(code="SAVE10_TEST", discount_percentage=10.0, is_used=False)
    db.add(discount)
    db.commit()
    db.close()
    
    item_id = setup_items[0]
    client.post(
        "/api/cart/add?user_id=test_user",
        json={"item_id": item_id, "quantity": 2}
    )
    response = client.post(
        "/api/checkout/",
        json={"user_id": "test_user", "discount_code": "SAVE10_TEST"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_amount"] == 20.0
    assert data["discount_amount"] == 2.0
    assert data["final_amount"] == 18.0

