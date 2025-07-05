"""
Performance monitoring and optimization endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
import psutil
import os

from ..database import get_db
from ..auth import get_current_user
from ..models import User
from ..optimizations import (
    get_database_stats, get_user_products_optimized,
    get_user_transactions_optimized, get_dashboard_summary_optimized
)
from ..logging_config import get_logger
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/performance", tags=["performance"])
limiter = Limiter(key_func=get_remote_address)
logger = get_logger("performance")


@router.get("/dashboard-optimized")
@limiter.limit("30/minute")
async def get_optimized_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get optimized dashboard data with performance monitoring
    """
    start_time = time.time()
    
    try:
        # Use optimized dashboard query
        dashboard_data = get_dashboard_summary_optimized(db, current_user.id)
        
        execution_time = time.time() - start_time
        
        logger.info(f"Dashboard data loaded for user {current_user.id} in {execution_time:.3f}s")
        
        return {
            "dashboard_data": dashboard_data,
            "performance": {
                "execution_time": execution_time,
                "user_id": current_user.id,
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Dashboard data loading failed for user {current_user.id} in {execution_time:.3f}s: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not load dashboard data: {str(e)}")


@router.get("/transactions-paginated")
@limiter.limit("60/minute")
async def get_paginated_transactions(
    request: Request,
    product_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get paginated transactions with performance optimization
    """
    start_time = time.time()
    
    try:
        # Validate limit and offset
        limit = min(max(limit, 1), 100)  # Between 1 and 100
        offset = max(offset, 0)
        
        # Use optimized transaction query
        transactions, total_count = get_user_transactions_optimized(
            db=db,
            user_id=current_user.id,
            product_id=product_id,
            transaction_type=transaction_type,
            limit=limit,
            offset=offset
        )
        
        execution_time = time.time() - start_time
        
        # Convert to dict format
        transaction_data = []
        for trans in transactions:
            transaction_data.append({
                "id": trans.id,
                "product_id": trans.product_id,
                "type": trans.type,
                "transaction_date": trans.transaction_date.isoformat(),
                "category": trans.category,
                "description": trans.description,
                "amount": float(trans.amount),
                "created_at": trans.created_at.isoformat(),
                "product": {
                    "id": trans.product.id,
                    "product_type": trans.product.product_type,
                    "identifier": trans.product.identifier,
                    "institution": {
                        "name": trans.product.institution.name
                    },
                    "currency": {
                        "code": trans.product.currency.code,
                        "symbol": trans.product.currency.symbol
                    }
                }
            })
        
        logger.info(f"Loaded {len(transactions)} transactions for user {current_user.id} in {execution_time:.3f}s")
        
        return {
            "transactions": transaction_data,
            "pagination": {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_next": offset + limit < total_count,
                "has_previous": offset > 0
            },
            "performance": {
                "execution_time": execution_time,
                "query_count": len(transactions),
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Paginated transactions loading failed for user {current_user.id} in {execution_time:.3f}s: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not load transactions: {str(e)}")


@router.get("/products-optimized")
@limiter.limit("60/minute")
async def get_optimized_products(
    request: Request,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get optimized products data with eager loading
    """
    start_time = time.time()
    
    try:
        # Use optimized products query
        products = get_user_products_optimized(db, current_user.id, include_inactive)
        
        execution_time = time.time() - start_time
        
        # Convert to dict format with eager-loaded data
        product_data = []
        for product in products:
            product_data.append({
                "id": product.id,
                "institution_id": product.institution_id,
                "product_type": product.product_type,
                "identifier": product.identifier,
                "balance": float(product.balance),
                "payment_due_day": product.payment_due_day,
                "is_active": product.is_active,
                "created_at": product.created_at.isoformat(),
                "institution": {
                    "id": product.institution.id,
                    "name": product.institution.name,
                    "logo_url": product.institution.logo_url
                },
                "currency": {
                    "id": product.currency.id,
                    "code": product.currency.code,
                    "name": product.currency.name,
                    "symbol": product.currency.symbol
                }
            })
        
        logger.info(f"Loaded {len(products)} products for user {current_user.id} in {execution_time:.3f}s")
        
        return {
            "products": product_data,
            "performance": {
                "execution_time": execution_time,
                "product_count": len(products),
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Optimized products loading failed for user {current_user.id} in {execution_time:.3f}s: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not load products: {str(e)}")


@router.get("/system-metrics")
@limiter.limit("10/minute")
async def get_system_metrics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get system performance metrics (admin/monitoring use)
    """
    start_time = time.time()
    
    try:
        # Get process info
        process = psutil.Process(os.getpid())
        
        # Memory usage
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        
        # CPU usage
        cpu_percent = process.cpu_percent(interval=1)
        
        # Database stats
        db_stats = get_database_stats(db)
        
        execution_time = time.time() - start_time
        
        logger.info(f"System metrics collected for user {current_user.id} in {execution_time:.3f}s")
        
        return {
            "system_metrics": {
                "memory": {
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                    "percent": memory_percent
                },
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "process": {
                    "pid": process.pid,
                    "status": process.status(),
                    "create_time": process.create_time(),
                    "num_threads": process.num_threads()
                }
            },
            "database_metrics": db_stats,
            "performance": {
                "execution_time": execution_time,
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"System metrics collection failed for user {current_user.id} in {execution_time:.3f}s: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not collect system metrics: {str(e)}")


@router.post("/cache/clear")
@limiter.limit("5/minute")
async def clear_application_cache(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Clear application caches (if using Redis or similar)
    """
    start_time = time.time()
    
    try:
        # Here you would implement cache clearing logic
        # For now, just log the action
        logger.info(f"Cache clear requested by user {current_user.id}")
        
        execution_time = time.time() - start_time
        
        return {
            "message": "Cache clearing initiated",
            "user_id": current_user.id,
            "performance": {
                "execution_time": execution_time,
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Cache clearing failed for user {current_user.id} in {execution_time:.3f}s: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not clear cache: {str(e)}")


@router.get("/health-detailed")
@limiter.limit("30/minute")
async def get_detailed_health(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed health information including performance metrics
    """
    start_time = time.time()
    
    try:
        # Test database connection with a simple query
        db.execute("SELECT 1")
        db_status = "healthy"
        
        # Get basic system info
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        
        execution_time = time.time() - start_time
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "status": db_status,
                "connection_time": execution_time
            },
            "system": {
                "memory": {
                    "total": memory_info.total,
                    "available": memory_info.available,
                    "percent": memory_info.percent
                },
                "disk": {
                    "total": disk_info.total,
                    "free": disk_info.free,
                    "percent": (disk_info.used / disk_info.total) * 100
                }
            },
            "api": {
                "version": "1.2.0",
                "uptime": time.time() - start_time,
                "features": [
                    "JWT Authentication",
                    "Rate Limiting",
                    "Response Compression",
                    "Database Optimizations",
                    "Performance Monitoring"
                ]
            },
            "performance": {
                "execution_time": execution_time,
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Detailed health check failed in {execution_time:.3f}s: {str(e)}")
        
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "performance": {
                "execution_time": execution_time,
                "generated_at": datetime.now().isoformat()
            }
        }