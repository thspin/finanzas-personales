import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app import models

# Test database URL
TEST_DATABASE_URL = "postgresql://finanzas_user:finanzas_pass@localhost/finanzas_test_db"

# Create test engine
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine"""
    models.Base.metadata.create_all(bind=engine)
    yield engine
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a fresh database session for each test"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = models.User(
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$test_hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_currency(db_session):
    """Create a test currency"""
    currency = models.Currency(
        code="USD",
        name="US Dollar",
        symbol="$"
    )
    db_session.add(currency)
    db_session.commit()
    db_session.refresh(currency)
    return currency


@pytest.fixture
def test_institution(db_session, test_user):
    """Create a test institution"""
    institution = models.Institution(
        user_id=test_user.id,
        name="Test Bank",
        logo_url="https://example.com/logo.png"
    )
    db_session.add(institution)
    db_session.commit()
    db_session.refresh(institution)
    return institution


@pytest.fixture
def test_product(db_session, test_user, test_institution, test_currency):
    """Create a test product"""
    product = models.Product(
        user_id=test_user.id,
        institution_id=test_institution.id,
        product_type="CHECKING_ACCOUNT",
        identifier="****1234",
        currency_id=test_currency.id,
        balance=1000.00,
        payment_due_day=15,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    # Login the test user
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass"}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    # If login fails, we need to create a proper test user with correct password
    from app.auth import get_password_hash
    test_user.hashed_password = get_password_hash("testpass")
    
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass"}
    )
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_category(db_session, test_user):
    """Create a test category"""
    category = models.Category(
        user_id=test_user.id,
        name="Test Category",
        type=models.CategoryType.EXPENSE,
        emoji="🏷️"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category