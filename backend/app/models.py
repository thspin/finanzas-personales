from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum, Numeric, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from .enums import (
    TransactionType,
    InstallmentStatus,
    CategoryType,
    ServiceFrequency,
    PaymentType,
    NotificationType
)

Base = declarative_base()

class Currency(Base):
    __tablename__ = "currencies"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    symbol = Column(String(5), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship("Product", back_populates="currency")
    services = relationship("Service", back_populates="currency")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    institutions = relationship("Institution", back_populates="user")
    products = relationship("Product", back_populates="user")
    categories = relationship("Category", back_populates="user")
    services = relationship("Service", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Institution(Base):
    __tablename__ = "institutions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    logo_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="institutions")
    products = relationship("Product", back_populates="institution")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    product_type = Column(String(50), nullable=False)
    identifier = Column(String(50), nullable=True)  # Número de cuenta o últimos 4 dígitos
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    balance = Column(Numeric(15, 2), nullable=False, default=0.00)
    payment_due_day = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="products")
    institution = relationship("Institution", back_populates="products")
    currency = relationship("Currency", back_populates="products")
    transactions = relationship("Transaction", back_populates="product")
    credits = relationship("Credit", back_populates="product")
    services = relationship("Service", back_populates="product")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    transaction_date = Column(Date, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="transactions")

class Credit(Base):
    __tablename__ = "credits"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    purchase_date = Column(Date, nullable=False)
    description = Column(String(255), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    total_installments = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="credits")
    installments = relationship("Installment", back_populates="credit")

class Installment(Base):
    __tablename__ = "installments"
    
    id = Column(Integer, primary_key=True, index=True)
    credit_id = Column(Integer, ForeignKey("credits.id"), nullable=False)
    installment_number = Column(Integer, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(Enum(InstallmentStatus), nullable=False, default=InstallmentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    credit = relationship("Credit", back_populates="installments")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False)
    type = Column(Enum(CategoryType), nullable=False)
    emoji = Column(String(10), nullable=True, default="📝")  # Emoji personalizable
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="categories")

class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)  # Nullable para servicios manuales
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    frequency = Column(Enum(ServiceFrequency), nullable=False, default=ServiceFrequency.MONTHLY)
    payment_day = Column(Integer, nullable=False)  # Día del mes (1-31)
    payment_type = Column(Enum(PaymentType), nullable=False, default=PaymentType.MANUAL)
    is_active = Column(Boolean, nullable=False, default=True)
    next_due_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="services")
    product = relationship("Product", back_populates="services")
    currency = relationship("Currency", back_populates="services")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    related_service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    related_product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="notifications")
    related_service = relationship("Service")
    related_product = relationship("Product")