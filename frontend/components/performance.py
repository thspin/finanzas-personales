"""
Performance optimization components for enhanced application speed
"""
import streamlit as st
import pandas as pd
import time
from typing import List, Dict, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json
from .api_client import get_api_client
from .ui_helpers import show_loading_spinner, show_progress_bar


# ============================================================================
# INTELLIGENT CACHING SYSTEM
# ============================================================================

def cache_key_generator(*args, **kwargs) -> str:
    """
    Generate a unique cache key based on function arguments
    
    Args:
        *args: Function arguments
        **kwargs: Function keyword arguments
    
    Returns:
        Unique cache key string
    """
    # Create a deterministic string from arguments
    key_data = {
        'args': str(args),
        'kwargs': sorted(kwargs.items()),
        'timestamp': datetime.now().strftime('%Y-%m-%d-%H')  # Hourly cache invalidation
    }
    
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


@st.cache_data(ttl=300)  # 5 minutes cache
def get_dashboard_data(user_token: str) -> Dict[str, Any]:
    """
    Cached dashboard data loading with intelligent invalidation
    
    Args:
        user_token: JWT token for API authentication
    
    Returns:
        Dictionary containing all dashboard data
    """
    api = get_api_client()
    
    try:
        # Load all dashboard data in parallel-like fashion
        with show_loading_spinner("Cargando datos del dashboard..."):
            dashboard_data = {
                'products': api.get_products(),
                'currencies': api.get_currencies(),
                'services': api.get_services(),
                'institutions': api.get_institutions(),
                'notification_count': api.get_notification_count(),
                'categories': api.get_categories(),
                'loaded_at': datetime.now().isoformat()
            }
            
            # Add computed metrics
            dashboard_data['metrics'] = compute_dashboard_metrics(dashboard_data)
            
            return dashboard_data
            
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
        return {}


@st.cache_data(ttl=600)  # 10 minutes cache for transactions
def get_transactions_cached(product_ids: List[int], limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Cached transaction loading with product filtering
    
    Args:
        product_ids: List of product IDs to fetch transactions for
        limit: Maximum number of transactions to fetch
    
    Returns:
        List of transactions
    """
    api = get_api_client()
    all_transactions = []
    
    try:
        for product_id in product_ids:
            try:
                transactions = api.get_transactions_by_product(product_id)
                all_transactions.extend(transactions)
            except:
                continue  # Skip products with errors
        
        # Sort by date (newest first) and apply limit
        all_transactions.sort(key=lambda x: x.get('transaction_date', ''), reverse=True)
        
        if limit:
            all_transactions = all_transactions[:limit]
            
        return all_transactions
        
    except Exception as e:
        st.error(f"Error loading transactions: {str(e)}")
        return []


@st.cache_data(ttl=900)  # 15 minutes cache for relatively static data
def get_master_data(user_token: str) -> Dict[str, Any]:
    """
    Cached master data (currencies, categories, institutions)
    
    Args:
        user_token: JWT token for API authentication
    
    Returns:
        Dictionary containing master data
    """
    api = get_api_client()
    
    try:
        return {
            'currencies': api.get_currencies(),
            'categories': api.get_categories(),
            'institutions': api.get_institutions(),
            'loaded_at': datetime.now().isoformat()
        }
    except Exception as e:
        st.error(f"Error loading master data: {str(e)}")
        return {}


def compute_dashboard_metrics(dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute dashboard metrics from loaded data
    
    Args:
        dashboard_data: Raw dashboard data
    
    Returns:
        Computed metrics dictionary
    """
    products = dashboard_data.get('products', [])
    services = dashboard_data.get('services', [])
    
    metrics = {
        'total_products': len(products),
        'active_products': len([p for p in products if p.get('is_active', True)]),
        'total_services': len(services),
        'active_services': len([s for s in services if s.get('is_active', True)]),
        'currencies_in_use': len(set(p.get('currency', {}).get('code') for p in products if p.get('currency'))),
        'upcoming_payments': len([s for s in services if is_payment_upcoming(s)])
    }
    
    # Calculate balances by currency
    balance_by_currency = {}
    for product in products:
        if not product.get('is_active', True):
            continue
            
        currency_code = product.get('currency', {}).get('code', 'USD')
        balance = product.get('balance', 0)
        
        if currency_code not in balance_by_currency:
            balance_by_currency[currency_code] = {
                'total': 0,
                'symbol': product.get('currency', {}).get('symbol', '$'),
                'products_count': 0
            }
        
        balance_by_currency[currency_code]['total'] += balance
        balance_by_currency[currency_code]['products_count'] += 1
    
    metrics['balance_by_currency'] = balance_by_currency
    
    return metrics


def is_payment_upcoming(service: Dict[str, Any], days_ahead: int = 30) -> bool:
    """
    Check if a service payment is upcoming
    
    Args:
        service: Service dictionary
        days_ahead: Number of days to look ahead
    
    Returns:
        True if payment is upcoming
    """
    if not service.get('is_active', True):
        return False
    
    next_due_date = service.get('next_due_date')
    if not next_due_date:
        return False
    
    try:
        due_date = datetime.fromisoformat(next_due_date.replace('Z', '+00:00')).date()
        today = datetime.now().date()
        days_until_due = (due_date - today).days
        
        return 0 <= days_until_due <= days_ahead
    except:
        return False


# ============================================================================
# EFFICIENT PAGINATION SYSTEM
# ============================================================================

class PaginationState:
    """Manage pagination state across components"""
    
    def __init__(self, key: str, items_per_page: int = 20):
        self.key = key
        self.items_per_page = items_per_page
        
        # Initialize session state
        if f"{key}_page" not in st.session_state:
            st.session_state[f"{key}_page"] = 1
        if f"{key}_items_per_page" not in st.session_state:
            st.session_state[f"{key}_items_per_page"] = items_per_page
    
    @property
    def current_page(self) -> int:
        return st.session_state[f"{self.key}_page"]
    
    @current_page.setter
    def current_page(self, value: int):
        st.session_state[f"{self.key}_page"] = max(1, value)
    
    @property
    def items_per_page(self) -> int:
        return st.session_state[f"{self.key}_items_per_page"]
    
    @items_per_page.setter
    def items_per_page(self, value: int):
        st.session_state[f"{self.key}_items_per_page"] = max(5, min(100, value))
        # Reset to first page when changing page size
        self.current_page = 1
    
    def get_slice(self, total_items: int) -> Tuple[int, int]:
        """Get start and end indices for current page"""
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        return start_idx, end_idx
    
    def get_total_pages(self, total_items: int) -> int:
        """Calculate total number of pages"""
        if total_items == 0:
            return 1
        return (total_items - 1) // self.items_per_page + 1


def render_pagination_controls(
    total_items: int,
    pagination_state: PaginationState,
    show_items_per_page: bool = True
) -> None:
    """
    Render pagination controls with page navigation
    
    Args:
        total_items: Total number of items
        pagination_state: Pagination state manager
        show_items_per_page: Whether to show items per page selector
    """
    if total_items == 0:
        return
    
    total_pages = pagination_state.get_total_pages(total_items)
    
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    
    with col1:
        if show_items_per_page:
            new_items_per_page = st.selectbox(
                "Por página:",
                [10, 20, 50, 100],
                index=[10, 20, 50, 100].index(pagination_state.items_per_page),
                key=f"{pagination_state.key}_items_select"
            )
            if new_items_per_page != pagination_state.items_per_page:
                pagination_state.items_per_page = new_items_per_page
                st.rerun()
    
    with col2:
        # Previous page button
        if st.button("← Anterior", disabled=pagination_state.current_page <= 1, key=f"{pagination_state.key}_prev"):
            pagination_state.current_page -= 1
            st.rerun()
    
    with col3:
        # Next page button
        if st.button("Siguiente →", disabled=pagination_state.current_page >= total_pages, key=f"{pagination_state.key}_next"):
            pagination_state.current_page += 1
            st.rerun()
    
    with col4:
        # Page info
        start_idx, end_idx = pagination_state.get_slice(total_items)
        st.markdown(f"**{start_idx + 1}-{end_idx}** de **{total_items}**")
    
    # Page number selector for large datasets
    if total_pages > 10:
        page_options = []
        current = pagination_state.current_page
        
        # Always include first and last pages
        page_options.extend([1, total_pages])
        
        # Include pages around current page
        for i in range(max(1, current - 2), min(total_pages + 1, current + 3)):
            page_options.append(i)
        
        # Remove duplicates and sort
        page_options = sorted(list(set(page_options)))
        
        selected_page = st.selectbox(
            f"Ir a página (1-{total_pages}):",
            page_options,
            index=page_options.index(current) if current in page_options else 0,
            key=f"{pagination_state.key}_jump"
        )
        
        if selected_page != pagination_state.current_page:
            pagination_state.current_page = selected_page
            st.rerun()


def render_transactions_paginated(
    transactions: List[Dict[str, Any]], 
    key: str = "transactions",
    items_per_page: int = 20
) -> None:
    """
    Render transactions with efficient pagination
    
    Args:
        transactions: List of transactions
        key: Unique key for pagination state
        items_per_page: Number of items per page
    """
    if not transactions:
        st.info("📝 No hay transacciones para mostrar")
        return
    
    # Initialize pagination
    pagination = PaginationState(key, items_per_page)
    
    # Render pagination controls at top
    st.markdown("### 📊 Controles de Paginación")
    render_pagination_controls(len(transactions), pagination)
    
    # Get current page data
    start_idx, end_idx = pagination.get_slice(len(transactions))
    current_page_transactions = transactions[start_idx:end_idx]
    
    # Render transactions table
    st.markdown(f"### 💰 Transacciones (Página {pagination.current_page})")
    
    if current_page_transactions:
        # Convert to DataFrame for better performance
        df_data = []
        for trans in current_page_transactions:
            df_data.append({
                'Fecha': trans.get('transaction_date', ''),
                'Tipo': '💰 Ingreso' if trans.get('type') == 'INCOME' else '💸 Egreso',
                'Categoría': trans.get('category', ''),
                'Descripción': trans.get('description', ''),
                'Monto': f"${trans.get('amount', 0):,.2f}"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Fecha': st.column_config.DateColumn('Fecha'),
                'Monto': st.column_config.TextColumn('Monto', help='Monto de la transacción')
            }
        )
    
    # Render pagination controls at bottom for large datasets
    if len(transactions) > 50:
        st.markdown("---")
        render_pagination_controls(len(transactions), pagination, show_items_per_page=False)


# ============================================================================
# LAZY LOADING SYSTEM
# ============================================================================

def progressive_data_loading(
    data_loaders: List[Tuple[str, Callable]], 
    show_progress: bool = True
) -> Dict[str, Any]:
    """
    Load data progressively with visual feedback
    
    Args:
        data_loaders: List of (name, loader_function) tuples
        show_progress: Whether to show progress bar
    
    Returns:
        Dictionary with loaded data
    """
    loaded_data = {}
    total_loaders = len(data_loaders)
    
    if show_progress:
        progress_container = st.empty()
        status_container = st.empty()
    
    for i, (name, loader_func) in enumerate(data_loaders):
        if show_progress:
            progress = (i + 1) / total_loaders
            progress_container.progress(progress, text=f"Cargando {name}...")
            status_container.info(f"📊 Procesando: {name}")
        
        try:
            start_time = time.time()
            data = loader_func()
            load_time = time.time() - start_time
            
            loaded_data[name] = {
                'data': data,
                'load_time': load_time,
                'loaded_at': datetime.now().isoformat()
            }
            
            if show_progress and load_time > 1.0:  # Show timing for slow operations
                status_container.success(f"✅ {name} cargado en {load_time:.2f}s")
        
        except Exception as e:
            loaded_data[name] = {
                'data': None,
                'error': str(e),
                'loaded_at': datetime.now().isoformat()
            }
            
            if show_progress:
                status_container.error(f"❌ Error cargando {name}: {str(e)}")
    
    if show_progress:
        progress_container.empty()
        status_container.empty()
    
    return loaded_data


@st.cache_data(ttl=60)  # 1 minute cache for frequently accessed data
def load_recent_activity(user_token: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Load recent activity with caching
    
    Args:
        user_token: JWT token for API authentication
        limit: Maximum number of recent activities
    
    Returns:
        List of recent activities
    """
    api = get_api_client()
    
    try:
        # Get recent transactions from all products
        products = api.get_products()
        recent_transactions = []
        
        for product in products[:5]:  # Limit to first 5 products for performance
            try:
                transactions = api.get_transactions_by_product(product['id'])
                # Get only the most recent ones
                transactions.sort(key=lambda x: x.get('transaction_date', ''), reverse=True)
                recent_transactions.extend(transactions[:2])  # 2 per product
            except:
                continue
        
        # Sort all by date and limit
        recent_transactions.sort(key=lambda x: x.get('transaction_date', ''), reverse=True)
        return recent_transactions[:limit]
        
    except Exception:
        return []


def lazy_load_component(
    component_name: str,
    loader_func: Callable,
    placeholder_text: str = "Cargando...",
    error_text: str = "Error al cargar datos"
) -> Any:
    """
    Lazy load a component with placeholder
    
    Args:
        component_name: Name of the component for caching
        loader_func: Function to load the component data
        placeholder_text: Text to show while loading
        error_text: Text to show on error
    
    Returns:
        Loaded component data or None
    """
    # Create a unique key for this component
    cache_key = f"lazy_load_{component_name}_{datetime.now().strftime('%Y%m%d%H')}"
    
    if cache_key not in st.session_state:
        # Show placeholder
        placeholder = st.empty()
        placeholder.info(f"🔄 {placeholder_text}")
        
        try:
            # Load data
            data = loader_func()
            st.session_state[cache_key] = data
            placeholder.empty()
            return data
        
        except Exception as e:
            placeholder.error(f"❌ {error_text}: {str(e)}")
            return None
    
    return st.session_state[cache_key]


# ============================================================================
# VIRTUAL SCROLLING FOR LARGE DATASETS
# ============================================================================

def render_virtual_list(
    items: List[Any],
    item_renderer: Callable[[Any, int], None],
    container_height: int = 400,
    item_height: int = 50,
    key: str = "virtual_list"
) -> None:
    """
    Render a virtual scrolling list for large datasets
    
    Args:
        items: List of items to render
        item_renderer: Function to render each item
        container_height: Height of the scrollable container
        item_height: Height of each item
        key: Unique key for the component
    """
    if not items:
        st.info("No hay elementos para mostrar")
        return
    
    total_items = len(items)
    visible_items = min(container_height // item_height, total_items)
    
    # Get scroll position from session state
    scroll_position = st.session_state.get(f"{key}_scroll", 0)
    
    # Calculate visible range
    start_index = max(0, scroll_position)
    end_index = min(start_index + visible_items, total_items)
    
    # Render scroll controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬆️ Subir", key=f"{key}_up", disabled=start_index <= 0):
            st.session_state[f"{key}_scroll"] = max(0, scroll_position - visible_items // 2)
            st.rerun()
    
    with col2:
        # Show current position
        st.markdown(f"**Mostrando {start_index + 1}-{end_index} de {total_items}**")
    
    with col3:
        if st.button("⬇️ Bajar", key=f"{key}_down", disabled=end_index >= total_items):
            st.session_state[f"{key}_scroll"] = min(total_items - visible_items, scroll_position + visible_items // 2)
            st.rerun()
    
    # Render visible items
    st.markdown("---")
    for i in range(start_index, end_index):
        item_renderer(items[i], i)


# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

def performance_monitor(func: Callable) -> Callable:
    """
    Decorator to monitor function performance
    
    Args:
        func: Function to monitor
    
    Returns:
        Wrapped function with performance monitoring
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log performance if it's slow
            if execution_time > 2.0:
                st.sidebar.warning(f"⚠️ {func.__name__} tardó {execution_time:.2f}s")
            elif execution_time > 5.0:
                st.sidebar.error(f"🐌 {func.__name__} muy lento: {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            st.sidebar.error(f"❌ {func.__name__} falló en {execution_time:.2f}s: {str(e)}")
            raise
    
    return wrapper


@st.cache_data(ttl=3600)  # 1 hour cache
def get_performance_metrics() -> Dict[str, Any]:
    """
    Get application performance metrics
    
    Returns:
        Dictionary with performance metrics
    """
    return {
        'cache_hits': len([key for key in st.session_state.keys() if 'cache' in key.lower()]),
        'session_keys': len(st.session_state.keys()),
        'current_time': datetime.now().isoformat(),
        'memory_usage': 'N/A',  # Would need psutil for real memory monitoring
        'page_load_time': time.time()
    }


def clear_performance_cache() -> None:
    """Clear all performance-related caches"""
    st.cache_data.clear()
    
    # Clear session state caches
    keys_to_remove = [key for key in st.session_state.keys() if 'cache' in key.lower() or 'lazy_load' in key.lower()]
    for key in keys_to_remove:
        del st.session_state[key]
    
    st.success("🧹 Cache limpiado exitosamente")
    st.rerun()