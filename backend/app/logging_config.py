import logging
import logging.config
import os
from datetime import datetime


def setup_logging():
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Get log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Logging configuration
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}',
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": f"{log_dir}/finanzas.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": f"{log_dir}/finanzas_errors.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "access_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": f"{log_dir}/access.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            "app": {
                "level": log_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False
            },
            "app.auth": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "app.database": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "app.api": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["access_file"],
                "propagate": False
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "error_file"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING",  # Only show warnings and errors for SQL
                "handlers": ["file"],
                "propagate": False
            }
        }
    }
    
    # Apply logging configuration
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Log startup message
    logger = logging.getLogger("app")
    logger.info(f"Logging initialized - Level: {log_level}")
    logger.info(f"Log files location: {os.path.abspath(log_dir)}")


class RequestLoggingMiddleware:
    """Middleware to log HTTP requests"""
    
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger("app.api")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Extract request info
            method = scope["method"]
            path = scope["path"]
            query_string = scope.get("query_string", b"").decode()
            client_ip = scope.get("client", ["unknown"])[0]
            
            # Log request start
            self.logger.info(f"Request started: {method} {path}?{query_string} from {client_ip}")
            
            # Store start time
            start_time = datetime.now()
            
            # Process request
            async def send_with_logging(message):
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                    end_time = datetime.now()
                    duration_ms = (end_time - start_time).total_seconds() * 1000
                    
                    # Log response
                    self.logger.info(
                        f"Request completed: {method} {path} - "
                        f"Status: {status_code} - Duration: {duration_ms:.2f}ms"
                    )
                
                await send(message)
            
            await self.app(scope, receive, send_with_logging)
        else:
            await self.app(scope, receive, send)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)


def log_user_action(user_id: int, action: str, details: str = None):
    """Log user actions for audit trail"""
    logger = get_logger("app.audit")
    message = f"User {user_id} performed action: {action}"
    if details:
        message += f" - Details: {details}"
    logger.info(message)


def log_error(error: Exception, context: str = None):
    """Log errors with context"""
    logger = get_logger("app.error")
    message = f"Error: {type(error).__name__}: {str(error)}"
    if context:
        message += f" - Context: {context}"
    logger.error(message, exc_info=True)


def log_database_operation(operation: str, table: str, user_id: int = None, record_id: int = None):
    """Log database operations"""
    logger = get_logger("app.database")
    message = f"Database {operation} on {table}"
    if user_id:
        message += f" by user {user_id}"
    if record_id:
        message += f" - Record ID: {record_id}"
    logger.info(message)