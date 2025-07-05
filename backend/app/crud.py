from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from passlib.context import CryptContext
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import List, Optional
from decimal import Decimal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Institution CRUD
def get_institutions(db: Session, user_id: int):
    return db.query(models.Institution).filter(models.Institution.user_id == user_id).all()

def get_institution(db: Session, institution_id: int, user_id: int):
    return db.query(models.Institution).filter(
        models.Institution.id == institution_id,
        models.Institution.user_id == user_id
    ).first()

def create_institution(db: Session, institution: schemas.InstitutionCreate, user_id: int):
    db_institution = models.Institution(**institution.dict(), user_id=user_id)
    db.add(db_institution)
    db.commit()
    db.refresh(db_institution)
    return db_institution

def delete_institution(db: Session, institution_id: int, user_id: int):
    institution = db.query(models.Institution).filter(
        models.Institution.id == institution_id,
        models.Institution.user_id == user_id
    ).first()
    
    if institution:
        db.delete(institution)
        db.commit()
        return True
    return False

# Product CRUD (ex-Account)
def get_products(db: Session, user_id: int):
    return db.query(models.Product).filter(models.Product.user_id == user_id).all()

def get_product(db: Session, product_id: int, user_id: int):
    return db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.user_id == user_id
    ).first()

def create_product(db: Session, product: schemas.ProductCreate, user_id: int):
    db_product = models.Product(**product.dict(), user_id=user_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product_balance(db: Session, product_id: int, amount: Decimal, is_income: bool):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        if is_income:
            product.balance += amount
        else:
            product.balance -= amount
        db.commit()
        db.refresh(product)
    return product

def delete_product(db: Session, product_id: int, user_id: int):
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.user_id == user_id
    ).first()
    
    if product:
        db.delete(product)
        db.commit()
        return True
    return False

# Transaction CRUD
def get_transactions(db: Session, product_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).filter(
        models.Transaction.product_id == product_id
    ).order_by(models.Transaction.transaction_date.desc()).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    # Update product balance
    is_income = transaction.type.value == "INCOME"
    update_product_balance(db, transaction.product_id, transaction.amount, is_income)
    
    return db_transaction

# Credit CRUD
def get_credits(db: Session, product_id: int):
    return db.query(models.Credit).filter(models.Credit.product_id == product_id).all()

def create_credit_with_installments(db: Session, credit: schemas.CreditCreate):
    db_credit = models.Credit(
        product_id=credit.product_id,
        purchase_date=credit.purchase_date,
        description=credit.description,
        total_amount=credit.total_amount,
        total_installments=credit.total_installments
    )
    db.add(db_credit)
    db.commit()
    db.refresh(db_credit)
    
    # Get product to determine payment due day
    product = db.query(models.Product).filter(models.Product.id == credit.product_id).first()
    payment_due_day = product.payment_due_day or 15  # Default to 15th if not set
    
    # Create installments
    installments = []
    for i in range(credit.total_installments):
        # Calculate installment amount
        if credit.installment_amounts and len(credit.installment_amounts) == credit.total_installments:
            installment_amount = credit.installment_amounts[i]
        else:
            installment_amount = credit.total_amount / credit.total_installments
        
        # Calculate due date
        due_date = credit.purchase_date + relativedelta(months=i+1)
        due_date = due_date.replace(day=payment_due_day)
        
        db_installment = models.Installment(
            credit_id=db_credit.id,
            installment_number=i + 1,
            amount=installment_amount,
            due_date=due_date
        )
        db.add(db_installment)
        installments.append(db_installment)
    
    db.commit()
    return db_credit

# Installment CRUD
def get_installments(db: Session, credit_id: int):
    return db.query(models.Installment).filter(
        models.Installment.credit_id == credit_id
    ).order_by(models.Installment.installment_number).all()

def get_pending_installments(db: Session, user_id: int):
    return db.query(models.Installment).join(models.Credit).join(models.Product).filter(
        models.Product.user_id == user_id,
        models.Installment.status == models.InstallmentStatus.PENDING
    ).order_by(models.Installment.due_date).all()

# Category CRUD
def get_categories(db: Session, user_id: int, category_type: Optional[str] = None):
    query = db.query(models.Category).filter(models.Category.user_id == user_id)
    if category_type:
        query = query.filter(models.Category.type == category_type)
    return query.order_by(models.Category.name).all()

def get_category(db: Session, category_id: int, user_id: int):
    return db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.user_id == user_id
    ).first()

def create_category(db: Session, category: schemas.CategoryCreate, user_id: int):
    db_category = models.Category(**category.dict(), user_id=user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int, user_id: int):
    category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.user_id == user_id
    ).first()
    
    if category:
        db.delete(category)
        db.commit()
        return True
    return False

def create_default_categories(db: Session, user_id: int):
    """Crear categorías predeterminadas para un nuevo usuario"""
    default_income_categories = [
        ("Sueldo", "💰"), ("Freelance", "💻"), ("Inversiones", "📈"), 
        ("Venta", "🛒"), ("Regalo", "🎁"), ("Bono", "🎉"), ("Otros", "💵")
    ]
    
    default_expense_categories = [
        ("Comida", "🍽️"), ("Transporte", "🚗"), ("Servicios", "💡"), 
        ("Entretenimiento", "🎬"), ("Salud", "🏥"), ("Educación", "📚"), 
        ("Ropa", "👕"), ("Casa", "🏠"), ("Tecnología", "📱"), ("Otros", "💸")
    ]
    
    # Crear categorías de ingresos
    for name, emoji in default_income_categories:
        category = models.Category(
            user_id=user_id,
            name=name,
            type=models.CategoryType.INCOME,
            emoji=emoji
        )
        db.add(category)
    
    # Crear categorías de egresos
    for name, emoji in default_expense_categories:
        category = models.Category(
            user_id=user_id,
            name=name,
            type=models.CategoryType.EXPENSE,
            emoji=emoji
        )
        db.add(category)
    
    db.commit()

# Currency CRUD
def get_currencies(db: Session):
    return db.query(models.Currency).order_by(models.Currency.code).all()

def get_currency(db: Session, currency_id: int):
    return db.query(models.Currency).filter(models.Currency.id == currency_id).first()

def get_currency_by_code(db: Session, code: str):
    return db.query(models.Currency).filter(models.Currency.code == code).first()

def create_currency(db: Session, currency: schemas.CurrencyCreate):
    db_currency = models.Currency(**currency.dict())
    db.add(db_currency)
    db.commit()
    db.refresh(db_currency)
    return db_currency

# Service CRUD
def get_services(db: Session, user_id: int, is_active: Optional[bool] = None):
    query = db.query(models.Service).filter(models.Service.user_id == user_id)
    if is_active is not None:
        query = query.filter(models.Service.is_active == is_active)
    return query.order_by(models.Service.next_due_date).all()

def get_service(db: Session, service_id: int, user_id: int):
    return db.query(models.Service).filter(
        models.Service.id == service_id,
        models.Service.user_id == user_id
    ).first()

def create_service(db: Session, service: schemas.ServiceCreate, user_id: int):
    db_service = models.Service(**service.dict(), user_id=user_id)
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def update_service(db: Session, service_id: int, service: schemas.ServiceCreate, user_id: int):
    db_service = db.query(models.Service).filter(
        models.Service.id == service_id,
        models.Service.user_id == user_id
    ).first()
    
    if db_service:
        for key, value in service.dict().items():
            setattr(db_service, key, value)
        db.commit()
        db.refresh(db_service)
    return db_service

def delete_service(db: Session, service_id: int, user_id: int):
    service = db.query(models.Service).filter(
        models.Service.id == service_id,
        models.Service.user_id == user_id
    ).first()
    
    if service:
        db.delete(service)
        db.commit()
        return True
    return False

def get_upcoming_services(db: Session, user_id: int, days_ahead: int = 7):
    """Obtener servicios que vencen en los próximos N días"""
    from datetime import date, timedelta
    end_date = date.today() + timedelta(days=days_ahead)
    
    return db.query(models.Service).filter(
        models.Service.user_id == user_id,
        models.Service.is_active == True,
        models.Service.next_due_date <= end_date,
        models.Service.next_due_date >= date.today()
    ).order_by(models.Service.next_due_date).all()

# Notification CRUD
def get_notifications(db: Session, user_id: int, is_read: Optional[bool] = None, limit: int = 50):
    query = db.query(models.Notification).filter(models.Notification.user_id == user_id)
    if is_read is not None:
        query = query.filter(models.Notification.is_read == is_read)
    return query.order_by(models.Notification.created_at.desc()).limit(limit).all()

def get_notification(db: Session, notification_id: int, user_id: int):
    return db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == user_id
    ).first()

def create_notification(db: Session, notification: schemas.NotificationCreate, user_id: int):
    db_notification = models.Notification(**notification.dict(), user_id=user_id)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def mark_notification_as_read(db: Session, notification_id: int, user_id: int):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == user_id
    ).first()
    
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification

def mark_all_notifications_as_read(db: Session, user_id: int):
    """Marcar todas las notificaciones como leídas"""
    notifications = db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.is_read == False
    ).all()
    
    for notification in notifications:
        notification.is_read = True
    
    db.commit()
    return len(notifications)

def delete_notification(db: Session, notification_id: int, user_id: int):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == user_id
    ).first()
    
    if notification:
        db.delete(notification)
        db.commit()
        return True
    return False

def get_unread_notifications_count(db: Session, user_id: int):
    """Obtener cantidad de notificaciones no leídas"""
    return db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.is_read == False
    ).count()

def create_service_due_notification(db: Session, service_id: int, user_id: int):
    """Crear notificación para vencimiento de servicio"""
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if service:
        notification = schemas.NotificationCreate(
            type=models.NotificationType.SERVICE_DUE,
            title=f"Vencimiento: {service.name}",
            message=f"Tu servicio {service.name} vence el {service.next_due_date}. Monto: {service.currency.symbol}{service.amount}",
            related_service_id=service_id,
            related_product_id=service.product_id
        )
        return create_notification(db, notification, user_id)
    return None