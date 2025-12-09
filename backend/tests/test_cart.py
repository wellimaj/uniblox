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

def test_add_to_cart(setup_items):
    item_id = setup_items[0]
    response = client.post(
        "/api/cart/add?user_id=test_user",
        json={"item_id": item_id, "quantity": 2}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["item_id"] == item_id
    assert data["quantity"] == 2

def test_get_cart(setup_items):
    item_id = setup_items[0]
    client.post(
        "/api/cart/add?user_id=test_user",
        json={"item_id": item_id, "quantity": 1}
    )
    response = client.get("/api/cart/test_user")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_remove_from_cart(setup_items):
    item_id = setup_items[0]
    client.post(
        "/api/cart/add?user_id=test_user",
        json={"item_id": item_id, "quantity": 1}
    )
    response = client.delete(f"/api/cart/test_user/item/{item_id}")
    assert response.status_code == 200
    cart_response = client.get("/api/cart/test_user")
    assert len(cart_response.json()) == 0

