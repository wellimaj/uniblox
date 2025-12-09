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
    db.add(item1)
    db.commit()
    db.refresh(item1)
    db.close()
    return item1.id

def test_admin_stats(setup_items):
    item_id = setup_items
    client.post(
        "/api/cart/add?user_id=test_user",
        json={"item_id": item_id, "quantity": 2}
    )
    client.post(
        "/api/checkout/",
        json={"user_id": "test_user", "discount_code": None}
    )
    response = client.get("/api/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_items_purchased"] >= 2
    assert data["total_purchase_amount"] >= 20.0

