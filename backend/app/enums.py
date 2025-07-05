from enum import Enum


class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class InstallmentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"


class CategoryType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class ServiceFrequency(str, Enum):
    MONTHLY = "MONTHLY"
    ANNUAL = "ANNUAL"
    WEEKLY = "WEEKLY"
    QUARTERLY = "QUARTERLY"


class PaymentType(str, Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"


class NotificationType(str, Enum):
    SERVICE_DUE = "SERVICE_DUE"
    LOW_BALANCE = "LOW_BALANCE"
    CREDIT_DUE = "CREDIT_DUE"
    GENERAL = "GENERAL"


class ProductType(str, Enum):
    CHECKING_ACCOUNT = "CHECKING_ACCOUNT"
    SAVINGS_ACCOUNT = "SAVINGS_ACCOUNT"
    CREDIT_CARD = "CREDIT_CARD"
    INVESTMENT = "INVESTMENT"
    LOAN = "LOAN"
    OTHER = "OTHER"