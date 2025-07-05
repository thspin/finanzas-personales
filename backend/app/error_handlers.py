import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose import JWTError
from .exceptions import FinanzasException
import traceback

# Setup logger
logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int, 
    message: str, 
    detail: str = None,
    error_code: str = None
) -> JSONResponse:
    """Create standardized error response"""
    content = {
        "error": True,
        "message": message,
        "status_code": status_code
    }
    
    if detail:
        content["detail"] = detail
    
    if error_code:
        content["error_code"] = error_code
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )


async def finanzas_exception_handler(request: Request, exc: FinanzasException):
    """Handle custom Finanzas exceptions"""
    logger.warning(f"Finanzas exception: {exc.message} - URL: {request.url}")
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error_code=exc.__class__.__name__
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc.detail} - URL: {request.url} - Status: {exc.status_code}")
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.detail or "An error occurred"
    )


async def jwt_exception_handler(request: Request, exc: JWTError):
    """Handle JWT-related exceptions"""
    logger.warning(f"JWT exception: {str(exc)} - URL: {request.url}")
    
    return create_error_response(
        status_code=401,
        message="Invalid or expired token",
        error_code="JWTError"
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database exceptions"""
    logger.error(f"Database exception: {str(exc)} - URL: {request.url}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Handle specific database errors
    if isinstance(exc, IntegrityError):
        # Extract constraint information if possible
        error_msg = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        
        if "unique constraint" in error_msg.lower():
            return create_error_response(
                status_code=409,
                message="Resource already exists",
                detail="A record with this information already exists",
                error_code="IntegrityError"
            )
        elif "foreign key constraint" in error_msg.lower():
            return create_error_response(
                status_code=400,
                message="Invalid reference",
                detail="Referenced resource does not exist",
                error_code="ForeignKeyError"
            )
    
    # Generic database error
    return create_error_response(
        status_code=500,
        message="Database operation failed",
        detail="An error occurred while processing your request",
        error_code="DatabaseError"
    )


async def validation_exception_handler(request: Request, exc: Exception):
    """Handle Pydantic validation exceptions"""
    logger.warning(f"Validation exception: {str(exc)} - URL: {request.url}")
    
    # Extract validation details if available
    detail = None
    if hasattr(exc, 'errors'):
        try:
            errors = exc.errors()
            detail = "; ".join([f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in errors])
        except:
            detail = str(exc)
    
    return create_error_response(
        status_code=422,
        message="Validation error",
        detail=detail or str(exc),
        error_code="ValidationError"
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)} - URL: {request.url}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return create_error_response(
        status_code=500,
        message="Internal server error",
        detail="An unexpected error occurred",
        error_code="InternalServerError"
    )


# Exception handlers mapping
EXCEPTION_HANDLERS = {
    FinanzasException: finanzas_exception_handler,
    HTTPException: http_exception_handler,
    JWTError: jwt_exception_handler,
    SQLAlchemyError: sqlalchemy_exception_handler,
    ValueError: validation_exception_handler,
    Exception: generic_exception_handler,
}