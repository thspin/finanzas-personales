"""
Database and API performance optimizations
"""
from fastapi import Depends
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import text, func, and_, or_, desc, asc
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import logging
from functools import lru_cache
import gzip
import json

from .database import get_db
from .models import (
    User, Institution, Product, Transaction, Credit, 
    Installment, Category, Currency, Service, Notification
)
from .auth import get_current_user

logger = logging.getLogger(__name__)


# ============================================================================
# OPTIMIZED DATABASE QUERIES
# ============================================================================

def get_user_products_optimized(
    db: Session, 
    user_id: int, 
    include_inactive: bool = False
) -> List[Product]:
    """
    Optimized query to get user products with related data
    
    Args:
        db: Database session
        user_id: User ID
        include_inactive: Whether to include inactive products
    
    Returns:
        List of products with eager-loaded relationships
    """
    query = db.query(Product).options(
        joinedload(Product.institution),
        joinedload(Product.currency)
    ).filter(Product.user_id == user_id)
    
    if not include_inactive:
        query = query.filter(Product.is_active == True)
    
    return query.order_by(Product.institution_id, Product.product_type).all()


def get_user_transactions_optimized(
    db: Session,
    user_id: int,
    product_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    transaction_type: Optional[str] = None,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0
) -> Tuple[List[Transaction], int]:
    """
    Optimized transaction query with filtering and pagination
    
    Args:
        db: Database session
        user_id: User ID
        product_id: Optional product filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        transaction_type: Optional transaction type filter
        limit: Maximum number of results
        offset: Offset for pagination
    
    Returns:
        Tuple of (transactions, total_count)
    """
    # Base query with joins
    base_query = db.query(Transaction).join(Product).options(
        joinedload(Transaction.product).joinedload(Product.institution),
        joinedload(Transaction.product).joinedload(Product.currency)
    ).filter(Product.user_id == user_id)
    
    # Apply filters
    if product_id:
        base_query = base_query.filter(Transaction.product_id == product_id)
    
    if start_date:
        base_query = base_query.filter(Transaction.transaction_date >= start_date)
    
    if end_date:
        base_query = base_query.filter(Transaction.transaction_date <= end_date)
    
    if transaction_type:
        base_query = base_query.filter(Transaction.type == transaction_type)
    
    # Get total count for pagination
    total_count = base_query.count()
    
    # Apply ordering, limit, and offset
    transactions = base_query.order_by(
        desc(Transaction.transaction_date),
        desc(Transaction.created_at)
    ).limit(limit).offset(offset).all()
    
    return transactions, total_count


def get_dashboard_summary_optimized(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Optimized dashboard summary with aggregated queries
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        Dictionary with dashboard summary data
    """
    # Get products with balances grouped by currency
    products_summary = db.query(
        Currency.code,
        Currency.symbol,
        Currency.name,
        func.count(Product.id).label('product_count'),
        func.sum(Product.balance).label('total_balance')
    ).join(Product).join(Currency).filter(
        Product.user_id == user_id,
        Product.is_active == True
    ).group_by(Currency.id).all()
    
    # Get recent transactions count by type
    recent_date = datetime.now().date() - timedelta(days=30)
    transactions_summary = db.query(
        Transaction.type,
        func.count(Transaction.id).label('count'),
        func.sum(Transaction.amount).label('total_amount')
    ).join(Product).filter(
        Product.user_id == user_id,
        Transaction.transaction_date >= recent_date
    ).group_by(Transaction.type).all()
    
    # Get upcoming services payments
    upcoming_payments = db.query(Service).filter(
        Service.user_id == user_id,
        Service.is_active == True,
        Service.next_due_date <= datetime.now().date() + timedelta(days=30)
    ).order_by(Service.next_due_date).limit(10).all()
    
    # Get notification count
    unread_notifications = db.query(func.count(Notification.id)).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).scalar()
    
    return {
        'products_by_currency': [
            {
                'currency_code': row.code,
                'currency_symbol': row.symbol,
                'currency_name': row.name,
                'product_count': row.product_count,
                'total_balance': float(row.total_balance or 0)
            }
            for row in products_summary
        ],
        'recent_transactions': [
            {
                'type': row.type,
                'count': row.count,
                'total_amount': float(row.total_amount or 0)
            }
            for row in transactions_summary
        ],
        'upcoming_payments_count': len(upcoming_payments),
        'unread_notifications': unread_notifications or 0,
        'generated_at': datetime.now().isoformat()
    }


def get_user_services_with_next_payments(
    db: Session, 
    user_id: int,
    days_ahead: int = 90
) -> List[Service]:
    """
    Get user services with upcoming payments optimized
    
    Args:
        db: Database session
        user_id: User ID
        days_ahead: How many days ahead to look for payments
    
    Returns:
        List of services with upcoming payments
    """
    future_date = datetime.now().date() + timedelta(days=days_ahead)
    
    return db.query(Service).options(
        joinedload(Service.currency),
        joinedload(Service.product).joinedload(Product.institution)
    ).filter(
        Service.user_id == user_id,
        Service.is_active == True,
        Service.next_due_date <= future_date
    ).order_by(Service.next_due_date).all()


def get_credit_installments_summary(
    db: Session,
    user_id: int,
    credit_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get credit installments summary with optimized queries
    
    Args:
        db: Database session
        user_id: User ID
        credit_id: Optional specific credit ID
    
    Returns:
        List of installment summaries
    """
    query = db.query(
        Credit.id.label('credit_id'),
        Credit.description,
        Credit.total_amount,
        Credit.total_installments,
        func.count(Installment.id).label('total_installments_count'),
        func.sum(
            func.case([(Installment.status == 'PAID', Installment.amount)], else_=0)
        ).label('paid_amount'),
        func.sum(
            func.case([(Installment.status == 'PENDING', Installment.amount)], else_=0)
        ).label('pending_amount'),
        func.min(
            func.case([(Installment.status == 'PENDING', Installment.due_date)], else_=None)
        ).label('next_due_date')
    ).join(Product).join(Installment).filter(
        Product.user_id == user_id
    )
    
    if credit_id:
        query = query.filter(Credit.id == credit_id)
    
    results = query.group_by(Credit.id).all()
    
    return [
        {
            'credit_id': row.credit_id,
            'description': row.description,
            'total_amount': float(row.total_amount),
            'total_installments': row.total_installments,
            'paid_amount': float(row.paid_amount or 0),
            'pending_amount': float(row.pending_amount or 0),
            'next_due_date': row.next_due_date.isoformat() if row.next_due_date else None,
            'completion_percentage': (float(row.paid_amount or 0) / float(row.total_amount)) * 100
        }
        for row in results
    ]


# ============================================================================
# CACHING UTILITIES
# ============================================================================

@lru_cache(maxsize=100)
def get_currencies_cached() -> List[Dict[str, Any]]:
    """
    Cached currency data (rarely changes)
    
    Returns:
        List of currencies
    """
    # This would be called with database session
    # Implementation depends on your caching strategy
    pass


def invalidate_user_cache(user_id: int) -> None:
    """
    Invalidate cache for a specific user
    
    Args:
        user_id: User ID to invalidate cache for
    """
    # Clear LRU caches
    get_currencies_cached.cache_clear()
    
    logger.info(f"Cache invalidated for user {user_id}")


# ============================================================================
# BULK OPERATIONS
# ============================================================================

def bulk_create_transactions(
    db: Session,
    transactions_data: List[Dict[str, Any]],
    user_id: int
) -> List[Transaction]:
    """
    Bulk create transactions for better performance
    
    Args:
        db: Database session
        transactions_data: List of transaction data
        user_id: User ID
    
    Returns:
        List of created transactions
    """
    # Validate that all products belong to the user
    product_ids = [data['product_id'] for data in transactions_data]
    valid_products = db.query(Product.id).filter(
        Product.id.in_(product_ids),
        Product.user_id == user_id
    ).all()
    valid_product_ids = {p.id for p in valid_products}
    
    # Filter valid transactions
    valid_transactions = [
        data for data in transactions_data 
        if data['product_id'] in valid_product_ids
    ]
    
    if not valid_transactions:
        return []
    
    # Bulk insert
    transactions = [Transaction(**data) for data in valid_transactions]
    db.add_all(transactions)
    db.commit()
    
    # Update product balances in bulk
    for transaction in transactions:
        product = db.query(Product).filter(Product.id == transaction.product_id).first()
        if product:
            if transaction.type == 'INCOME':
                product.balance += transaction.amount
            else:  # EXPENSE
                product.balance -= transaction.amount
    
    db.commit()
    
    return transactions


def bulk_update_installment_status(
    db: Session,
    installment_updates: List[Dict[str, Any]],
    user_id: int
) -> int:
    """
    Bulk update installment statuses
    
    Args:
        db: Database session
        installment_updates: List of {installment_id, status} dictionaries
        user_id: User ID for security
    
    Returns:
        Number of updated installments
    """
    installment_ids = [update['installment_id'] for update in installment_updates]
    
    # Verify all installments belong to the user
    valid_installments = db.query(Installment.id).join(Credit).join(Product).filter(
        Installment.id.in_(installment_ids),
        Product.user_id == user_id
    ).all()
    valid_ids = {inst.id for inst in valid_installments}
    
    updated_count = 0
    for update in installment_updates:
        if update['installment_id'] in valid_ids:
            db.query(Installment).filter(
                Installment.id == update['installment_id']
            ).update({'status': update['status']})
            updated_count += 1
    
    db.commit()
    return updated_count


# ============================================================================
# DATABASE INDEXING SUGGESTIONS
# ============================================================================

def get_index_suggestions() -> List[str]:
    """
    Get database indexing suggestions for better performance
    
    Returns:
        List of SQL statements to create indexes
    """
    return [
        # User-based indexes
        "CREATE INDEX IF NOT EXISTS idx_products_user_active ON products(user_id, is_active);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_product_date ON transactions(product_id, transaction_date DESC);",
        "CREATE INDEX IF NOT EXISTS idx_services_user_active_due ON services(user_id, is_active, next_due_date);",
        "CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);",
        
        # Performance indexes
        "CREATE INDEX IF NOT EXISTS idx_transactions_type_date ON transactions(type, transaction_date DESC);",
        "CREATE INDEX IF NOT EXISTS idx_installments_status_due ON installments(status, due_date);",
        "CREATE INDEX IF NOT EXISTS idx_products_currency ON products(currency_id);",
        
        # Composite indexes for complex queries
        "CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(product_id, transaction_date DESC, type);",
        "CREATE INDEX IF NOT EXISTS idx_credits_product_date ON credits(product_id, purchase_date DESC);",
    ]


def apply_database_optimizations(db: Session) -> None:
    """
    Apply database optimizations (indexes, etc.)
    
    Args:
        db: Database session
    """
    suggestions = get_index_suggestions()
    
    for index_sql in suggestions:
        try:
            db.execute(text(index_sql))
            logger.info(f"Applied optimization: {index_sql[:50]}...")
        except Exception as e:
            logger.warning(f"Could not apply optimization {index_sql[:50]}...: {str(e)}")
    
    db.commit()


# ============================================================================
# QUERY ANALYSIS AND MONITORING
# ============================================================================

def log_slow_query(query_description: str, execution_time: float, threshold: float = 1.0) -> None:
    """
    Log slow queries for performance monitoring
    
    Args:
        query_description: Description of the query
        execution_time: Time taken to execute
        threshold: Threshold for considering a query slow
    """
    if execution_time > threshold:
        logger.warning(
            f"SLOW QUERY: {query_description} took {execution_time:.3f}s "
            f"(threshold: {threshold}s)"
        )


def get_database_stats(db: Session) -> Dict[str, Any]:
    """
    Get database performance statistics
    
    Args:
        db: Database session
    
    Returns:
        Dictionary with database statistics
    """
    try:
        # Get table sizes
        table_stats = db.execute(text("""
            SELECT 
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation
            FROM pg_stats 
            WHERE schemaname = 'public'
            ORDER BY tablename, attname;
        """)).fetchall()
        
        # Get index usage
        index_stats = db.execute(text("""
            SELECT 
                indexrelname,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes
            ORDER BY idx_tup_read DESC;
        """)).fetchall()
        
        return {
            'table_stats': [dict(row._mapping) for row in table_stats],
            'index_stats': [dict(row._mapping) for row in index_stats],
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Could not get database stats: {str(e)}")
        return {
            'error': str(e),
            'generated_at': datetime.now().isoformat()
        }


# ============================================================================
# RESPONSE COMPRESSION
# ============================================================================

def compress_response_data(data: Any) -> bytes:
    """
    Compress response data using gzip
    
    Args:
        data: Data to compress (will be JSON serialized)
    
    Returns:
        Compressed data as bytes
    """
    json_data = json.dumps(data, default=str).encode('utf-8')
    return gzip.compress(json_data)


def decompress_response_data(compressed_data: bytes) -> Any:
    """
    Decompress response data
    
    Args:
        compressed_data: Compressed data bytes
    
    Returns:
        Decompressed data
    """
    json_data = gzip.decompress(compressed_data).decode('utf-8')
    return json.loads(json_data)


# ============================================================================
# MEMORY OPTIMIZATION
# ============================================================================

def optimize_query_memory(query_result: List[Any], batch_size: int = 1000):
    """
    Generator to process large query results in batches
    
    Args:
        query_result: Large query result
        batch_size: Size of each batch
    
    Yields:
        Batches of results
    """
    for i in range(0, len(query_result), batch_size):
        yield query_result[i:i + batch_size]


def stream_large_dataset(
    db: Session,
    query,
    batch_size: int = 1000
):
    """
    Stream large datasets to avoid memory issues
    
    Args:
        db: Database session
        query: SQLAlchemy query object
        batch_size: Size of each batch
    
    Yields:
        Batches of query results
    """
    offset = 0
    while True:
        batch = query.limit(batch_size).offset(offset).all()
        if not batch:
            break
        yield batch
        offset += batch_size