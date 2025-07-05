from pydantic import BaseModel, EmailStr
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime
from .enums import (
    TransactionType,
    InstallmentStatus,
    CategoryType,
    ServiceFrequency,
    PaymentType,
    NotificationType
)

# Currency Schemas
class CurrencyBase(BaseModel):
    code: str
    name: str
    symbol: str

class CurrencyCreate(CurrencyBase):
    pass

class Currency(CurrencyBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Institution Schemas
class InstitutionBase(BaseModel):
    name: str
    logo_url: Optional[str] = None

class InstitutionCreate(InstitutionBase):
    pass

class Institution(InstitutionBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Product Schemas (ex-Account)
class ProductBase(BaseModel):
    institution_id: int
    product_type: str
    identifier: Optional[str] = None  # Número de cuenta o últimos 4 dígitos
    currency_id: int
    payment_due_day: Optional[int] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    user_id: int
    balance: Decimal
    created_at: datetime
    currency: Currency
    institution: Institution
    
    class Config:
        from_attributes = True

# Transaction Schemas
class TransactionBase(BaseModel):
    type: TransactionType
    transaction_date: date
    category: str
    description: Optional[str] = None
    amount: Decimal

class TransactionCreate(TransactionBase):
    product_id: int

class Transaction(TransactionBase):
    id: int
    product_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Credit Schemas
class CreditBase(BaseModel):
    purchase_date: date
    description: str
    total_amount: Decimal
    total_installments: int

class CreditCreate(CreditBase):
    product_id: int
    installment_amounts: Optional[List[Decimal]] = None

class Credit(CreditBase):
    id: int
    product_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Installment Schemas
class InstallmentBase(BaseModel):
    installment_number: int
    amount: Decimal
    due_date: date
    status: InstallmentStatus = InstallmentStatus.PENDING

class Installment(InstallmentBase):
    id: int
    credit_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    type: CategoryType
    emoji: Optional[str] = "📝"

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Service Schemas
class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    amount: Decimal
    currency_id: int
    frequency: ServiceFrequency = ServiceFrequency.MONTHLY
    payment_day: int
    payment_type: PaymentType = PaymentType.MANUAL
    is_active: bool = True
    next_due_date: date
    product_id: Optional[int] = None

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    id: int
    user_id: int
    created_at: datetime
    currency: Currency
    product: Optional["Product"] = None  # Forward reference
    
    class Config:
        from_attributes = True

# Notification Schemas
class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    message: str
    is_read: bool = False
    related_service_id: Optional[int] = None
    related_product_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: User