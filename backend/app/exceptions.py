from fastapi import HTTPException, status


class FinanzasException(Exception):
    """Base exception for Finanzas app"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(FinanzasException):
    """Resource not found exception"""
    def __init__(self, resource: str, identifier: str = None):
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        else:
            message = f"{resource} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ValidationError(FinanzasException):
    """Validation error exception"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class AuthenticationError(FinanzasException):
    """Authentication error exception"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(FinanzasException):
    """Authorization error exception"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ConflictError(FinanzasException):
    """Conflict error exception"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_409_CONFLICT)


class DatabaseError(FinanzasException):
    """Database operation error exception"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class BusinessLogicError(FinanzasException):
    """Business logic error exception"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


# Specific domain exceptions
class UserNotFoundError(NotFoundError):
    def __init__(self, user_id: str = None):
        super().__init__("User", user_id)


class InstitutionNotFoundError(NotFoundError):
    def __init__(self, institution_id: str = None):
        super().__init__("Institution", institution_id)


class ProductNotFoundError(NotFoundError):
    def __init__(self, product_id: str = None):
        super().__init__("Product", product_id)


class CurrencyNotFoundError(NotFoundError):
    def __init__(self, currency_id: str = None):
        super().__init__("Currency", currency_id)


class CategoryNotFoundError(NotFoundError):
    def __init__(self, category_id: str = None):
        super().__init__("Category", category_id)


class ServiceNotFoundError(NotFoundError):
    def __init__(self, service_id: str = None):
        super().__init__("Service", service_id)


class CreditNotFoundError(NotFoundError):
    def __init__(self, credit_id: str = None):
        super().__init__("Credit", credit_id)


class NotificationNotFoundError(NotFoundError):
    def __init__(self, notification_id: str = None):
        super().__init__("Notification", notification_id)


class InsufficientBalanceError(BusinessLogicError):
    def __init__(self, available: float, required: float):
        message = f"Insufficient balance. Available: {available}, Required: {required}"
        super().__init__(message)


class InvalidTransactionTypeError(ValidationError):
    def __init__(self, transaction_type: str):
        message = f"Invalid transaction type: {transaction_type}"
        super().__init__(message)


class InvalidProductTypeError(ValidationError):
    def __init__(self, product_type: str, operation: str):
        message = f"Product type '{product_type}' is not valid for operation: {operation}"
        super().__init__(message)


class DuplicateResourceError(ConflictError):
    def __init__(self, resource: str, field: str, value: str):
        message = f"{resource} with {field} '{value}' already exists"
        super().__init__(message)


class InvalidDateRangeError(ValidationError):
    def __init__(self, start_date: str, end_date: str):
        message = f"Invalid date range: start_date ({start_date}) must be before end_date ({end_date})"
        super().__init__(message)


class InvalidInstallmentError(ValidationError):
    def __init__(self, message: str):
        super().__init__(f"Invalid installment configuration: {message}")


class UnauthorizedAccessError(AuthorizationError):
    def __init__(self, resource: str):
        message = f"You don't have permission to access this {resource}"
        super().__init__(message)