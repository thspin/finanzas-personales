"""
UI Helper components for enhanced user experience
"""
import streamlit as st
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import re


# ============================================================================
# LOADING STATES AND FEEDBACK
# ============================================================================

def show_loading_spinner(message: str = "Cargando...", key: Optional[str] = None):
    """
    Reusable loading spinner for async operations
    
    Args:
        message: Loading message to display
        key: Unique key for the spinner
    
    Returns:
        Context manager for spinner
    """
    return st.spinner(message)


def show_success_message(message: str, duration: int = 3, key: Optional[str] = None):
    """
    Toast success message with auto-dismiss
    
    Args:
        message: Success message to display
        duration: Duration in seconds to show message
        key: Unique key for the message
    """
    success_container = st.empty()
    success_container.success(message)
    
    # Auto-dismiss after duration (simulated)
    # Note: Streamlit doesn't have native auto-dismiss, 
    # so we use session state to manage this
    if key:
        dismiss_key = f"dismiss_{key}_{int(time.time())}"
        if dismiss_key not in st.session_state:
            st.session_state[dismiss_key] = True
            # In a real implementation, you might use JavaScript or 
            # a more sophisticated state management approach


def show_error_message(message: str, details: Optional[str] = None, key: Optional[str] = None):
    """
    Alert error message with optional details
    
    Args:
        message: Main error message
        details: Optional detailed error information
        key: Unique key for the message
    """
    if details:
        with st.expander(f"❌ {message}", expanded=True):
            st.error(message)
            st.code(details, language="text")
    else:
        st.error(f"❌ {message}")


def show_warning_message(message: str, key: Optional[str] = None):
    """
    Warning message for user attention
    
    Args:
        message: Warning message to display
        key: Unique key for the message
    """
    st.warning(f"⚠️ {message}")


def show_info_message(message: str, key: Optional[str] = None):
    """
    Info message for user guidance
    
    Args:
        message: Info message to display
        key: Unique key for the message
    """
    st.info(f"💡 {message}")


def show_progress_bar(current: int, total: int, message: str = "Progreso"):
    """
    Show progress bar for long operations
    
    Args:
        current: Current progress value
        total: Total value
        message: Progress message
    """
    progress = current / total if total > 0 else 0
    st.progress(progress, text=f"{message}: {current}/{total}")


# ============================================================================
# REAL-TIME VALIDATIONS
# ============================================================================

def validate_amount_real_time(amount: float, min_amount: float = 0.01, max_amount: float = 999999999.99) -> Dict[str, Any]:
    """
    Validate amount while user types
    
    Args:
        amount: Amount to validate
        min_amount: Minimum allowed amount
        max_amount: Maximum allowed amount
    
    Returns:
        Dict with validation result
    """
    if amount is None:
        return {"valid": False, "message": "Ingresa un monto", "level": "info"}
    
    if amount <= 0:
        return {"valid": False, "message": "El monto debe ser mayor a 0", "level": "error"}
    
    if amount < min_amount:
        return {"valid": False, "message": f"Monto mínimo: ${min_amount:,.2f}", "level": "error"}
    
    if amount > max_amount:
        return {"valid": False, "message": f"Monto máximo: ${max_amount:,.2f}", "level": "error"}
    
    return {"valid": True, "message": f"✅ Monto válido: ${amount:,.2f}", "level": "success"}


def validate_email_format(email: str) -> Dict[str, Any]:
    """
    Validate email format in real time
    
    Args:
        email: Email to validate
    
    Returns:
        Dict with validation result
    """
    if not email:
        return {"valid": False, "message": "Ingresa un email", "level": "info"}
    
    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return {"valid": False, "message": "Formato de email inválido", "level": "error"}
    
    return {"valid": True, "message": "✅ Email válido", "level": "success"}


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength in real time
    
    Args:
        password: Password to validate
    
    Returns:
        Dict with validation result and strength info
    """
    if not password:
        return {"valid": False, "message": "Ingresa una contraseña", "level": "info", "strength": 0}
    
    strength = 0
    messages = []
    
    # Length check
    if len(password) >= 8:
        strength += 1
        messages.append("✅ Al menos 8 caracteres")
    else:
        messages.append("❌ Mínimo 8 caracteres")
    
    # Uppercase check
    if re.search(r'[A-Z]', password):
        strength += 1
        messages.append("✅ Contiene mayúsculas")
    else:
        messages.append("❌ Agregar mayúsculas")
    
    # Lowercase check
    if re.search(r'[a-z]', password):
        strength += 1
        messages.append("✅ Contiene minúsculas")
    else:
        messages.append("❌ Agregar minúsculas")
    
    # Number check
    if re.search(r'\d', password):
        strength += 1
        messages.append("✅ Contiene números")
    else:
        messages.append("❌ Agregar números")
    
    # Special character check
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        strength += 1
        messages.append("✅ Contiene símbolos")
    else:
        messages.append("❌ Agregar símbolos")
    
    # Determine strength level
    if strength >= 4:
        level = "success"
        strength_text = "Fuerte"
    elif strength >= 3:
        level = "warning"
        strength_text = "Media"
    else:
        level = "error"
        strength_text = "Débil"
    
    return {
        "valid": strength >= 3,
        "message": f"Fortaleza: {strength_text} ({strength}/5)",
        "level": level,
        "strength": strength,
        "details": messages
    }


def check_duplicate_transaction(
    description: str, 
    amount: float, 
    transaction_date: date,
    existing_transactions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Detect potentially duplicate transactions
    
    Args:
        description: Transaction description
        amount: Transaction amount
        transaction_date: Transaction date
        existing_transactions: List of existing transactions
    
    Returns:
        Dict with duplicate check result
    """
    if not existing_transactions:
        return {"duplicate": False, "message": ""}
    
    # Check for similar transactions in the last 30 days
    date_threshold = transaction_date
    potential_duplicates = []
    
    for trans in existing_transactions:
        # Parse transaction date
        try:
            trans_date = datetime.fromisoformat(trans['transaction_date'].replace('Z', '+00:00')).date()
        except:
            continue
        
        # Check if within 30 days
        days_diff = abs((transaction_date - trans_date).days)
        if days_diff > 30:
            continue
        
        # Check amount similarity (exact match or very close)
        amount_diff = abs(float(trans['amount']) - amount)
        amount_similar = amount_diff < 0.01 or (amount_diff / amount) < 0.05
        
        # Check description similarity (basic text matching)
        desc_similar = False
        if description and trans.get('description'):
            # Simple similarity check
            desc1 = description.lower().strip()
            desc2 = trans['description'].lower().strip()
            desc_similar = desc1 == desc2 or (
                len(desc1) > 3 and len(desc2) > 3 and (desc1 in desc2 or desc2 in desc1)
            )
        
        # If both amount and description are similar, it's a potential duplicate
        if amount_similar and (desc_similar or days_diff == 0):
            potential_duplicates.append({
                "transaction": trans,
                "similarity": "high" if desc_similar and days_diff == 0 else "medium"
            })
    
    if potential_duplicates:
        duplicate_info = potential_duplicates[0]  # Most likely duplicate
        return {
            "duplicate": True,
            "message": f"⚠️ Posible duplicado: ${duplicate_info['transaction']['amount']:,.2f} - {duplicate_info['transaction'].get('description', 'Sin descripción')}",
            "level": "warning",
            "similar_transaction": duplicate_info['transaction']
        }
    
    return {"duplicate": False, "message": ""}


def validate_required_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate multiple required fields
    
    Args:
        fields: Dict with field_name: value pairs
    
    Returns:
        Dict with validation results
    """
    missing_fields = []
    
    for field_name, value in fields.items():
        if value is None or value == "" or (isinstance(value, str) and not value.strip()):
            missing_fields.append(field_name)
    
    if missing_fields:
        return {
            "valid": False,
            "message": f"Campos requeridos: {', '.join(missing_fields)}",
            "level": "error",
            "missing_fields": missing_fields
        }
    
    return {"valid": True, "message": "✅ Todos los campos completos", "level": "success"}


# ============================================================================
# ENHANCED NAVIGATION
# ============================================================================

def render_breadcrumbs(current_page: str, page_hierarchy: List[str]):
    """
    Render breadcrumbs for clear navigation
    
    Args:
        current_page: Current page name
        page_hierarchy: List of parent pages
    """
    breadcrumb_items = []
    for page in page_hierarchy:
        breadcrumb_items.append(page)
    breadcrumb_items.append(f"**{current_page}**")
    
    breadcrumb_text = " → ".join(breadcrumb_items)
    st.markdown(f"🏠 {breadcrumb_text}")


def sidebar_navigation_enhanced(
    menu_options: Dict[str, str], 
    current_page: str,
    notifications_count: int = 0
):
    """
    Enhanced sidebar navigation with icons, badges and active state
    
    Args:
        menu_options: Dict of menu items {display_name: page_key}
        current_page: Current active page
        notifications_count: Number of unread notifications
    
    Returns:
        Selected page
    """
    st.sidebar.title("📊 Panel de Control")
    
    # Add notifications badge if there are any
    if notifications_count > 0:
        st.sidebar.markdown(f"🔔 **{notifications_count} notificaciones**")
        st.sidebar.markdown("---")
    
    # Get current index based on current_page
    page_keys = list(menu_options.values())
    try:
        current_index = page_keys.index(current_page)
    except ValueError:
        current_index = 0  # Default to first option
    
    # Enhanced menu with icons and active state indicators
    enhanced_options = []
    for display_name, page_key in menu_options.items():
        if page_key == current_page:
            enhanced_options.append(f"**▶ {display_name}**")  # Active indicator
        else:
            enhanced_options.append(display_name)
    
    # Use selectbox instead of radio for better behavior
    selected_index = st.sidebar.selectbox(
        "Navegar a:",
        range(len(enhanced_options)),
        format_func=lambda x: enhanced_options[x],
        index=current_index,
        key="navigation_select"
    )
    
    # Return the actual page key
    return page_keys[selected_index]


def quick_actions_sidebar():
    """
    Quick actions in sidebar for common operations
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Acciones Rápidas")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("💰", help="Nueva Transacción", key="quick_transaction"):
            st.session_state.quick_action = "transaction"
            # No usar st.rerun() aqui, dejar que main.py maneje
    
    with col2:
        if st.button("🏧", help="Nuevo Crédito", key="quick_credit"):
            st.session_state.quick_action = "credit"
            # No usar st.rerun() aqui, dejar que main.py maneje


def search_functionality(searchable_data: List[Dict[str, Any]], search_fields: List[str]):
    """
    Global search functionality for transactions and products
    
    Args:
        searchable_data: List of items to search through
        search_fields: List of fields to search in
    
    Returns:
        Filtered data based on search
    """
    search_query = st.text_input(
        "🔍 Buscar...", 
        placeholder="Buscar transacciones, productos, servicios...",
        key="global_search"
    )
    
    if not search_query:
        return searchable_data
    
    filtered_data = []
    search_query_lower = search_query.lower()
    
    for item in searchable_data:
        for field in search_fields:
            if field in item and item[field]:
                field_value = str(item[field]).lower()
                if search_query_lower in field_value:
                    filtered_data.append(item)
                    break
    
    if filtered_data:
        st.info(f"🔍 {len(filtered_data)} resultados encontrados para '{search_query}'")
    else:
        st.warning(f"🔍 No se encontraron resultados para '{search_query}'")
    
    return filtered_data


# ============================================================================
# FORM ENHANCEMENTS
# ============================================================================

def enhanced_number_input(
    label: str,
    min_value: float = 0.0,
    max_value: float = 999999999.99,
    step: float = 0.01,
    format_str: str = "%.2f",
    key: Optional[str] = None,
    help_text: Optional[str] = None,
    currency_symbol: str = "$"
):
    """
    Enhanced number input with real-time validation
    
    Args:
        label: Input label
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        step: Step increment
        format_str: Number format
        key: Unique key
        help_text: Help text
        currency_symbol: Currency symbol to display
    
    Returns:
        Tuple of (value, validation_result)
    """
    value = st.number_input(
        label,
        min_value=min_value,
        max_value=max_value,
        step=step,
        format=format_str,
        key=key,
        help=help_text
    )
    
    # Real-time validation
    validation = validate_amount_real_time(value, min_value, max_value)
    
    # Show validation message
    if validation["level"] == "error":
        st.error(validation["message"])
    elif validation["level"] == "warning":
        st.warning(validation["message"])
    elif validation["level"] == "success" and value > 0:
        st.success(validation["message"])
    
    return value, validation


def enhanced_text_input(
    label: str,
    placeholder: str = "",
    max_chars: Optional[int] = None,
    key: Optional[str] = None,
    validation_func: Optional[callable] = None,
    help_text: Optional[str] = None
):
    """
    Enhanced text input with real-time validation
    
    Args:
        label: Input label
        placeholder: Placeholder text
        max_chars: Maximum characters allowed
        key: Unique key
        validation_func: Function to validate input
        help_text: Help text
    
    Returns:
        Tuple of (value, validation_result)
    """
    value = st.text_input(
        label,
        placeholder=placeholder,
        max_chars=max_chars,
        key=key,
        help=help_text
    )
    
    validation = {"valid": True, "message": "", "level": "info"}
    
    # Apply validation function if provided
    if validation_func and value:
        validation = validation_func(value)
        
        # Show validation message
        if validation["level"] == "error":
            st.error(validation["message"])
        elif validation["level"] == "warning":
            st.warning(validation["message"])
        elif validation["level"] == "success":
            st.success(validation["message"])
    
    return value, validation


def enhanced_selectbox(
    label: str,
    options: List[Any],
    format_func: Optional[callable] = None,
    key: Optional[str] = None,
    help_text: Optional[str] = None,
    empty_label: str = "Seleccionar..."
):
    """
    Enhanced selectbox with better UX
    
    Args:
        label: Selectbox label
        options: List of options
        format_func: Function to format options
        key: Unique key
        help_text: Help text
        empty_label: Label for empty selection
    
    Returns:
        Selected value (None if empty selection)
    """
    # Add empty option at the beginning
    enhanced_options = [None] + list(options)
    
    def enhanced_format_func(option):
        if option is None:
            return empty_label
        if format_func:
            return format_func(option)
        return str(option)
    
    selected = st.selectbox(
        label,
        enhanced_options,
        format_func=enhanced_format_func,
        key=key,
        help=help_text
    )
    
    return selected


# ============================================================================
# DATA VISUALIZATION ENHANCEMENTS
# ============================================================================

def render_metric_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    help_text: Optional[str] = None
):
    """
    Render enhanced metric card
    
    Args:
        title: Metric title
        value: Metric value
        delta: Change indicator
        delta_color: Delta color (normal, inverse, off)
        help_text: Help text
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )


def render_status_badge(status: str, status_config: Dict[str, Dict[str, str]]):
    """
    Render status badge with colors
    
    Args:
        status: Status value
        status_config: Configuration for status display
    """
    config = status_config.get(status, {"color": "gray", "icon": "⚪", "text": status})
    
    st.markdown(
        f"""
        <span style="
            background-color: {config['color']};
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            font-weight: bold;
        ">
            {config['icon']} {config['text']}
        </span>
        """,
        unsafe_allow_html=True
    )


def render_progress_indicator(current: int, total: int, label: str = "Progreso"):
    """
    Render progress indicator with percentage
    
    Args:
        current: Current value
        total: Total value
        label: Progress label
    """
    percentage = (current / total * 100) if total > 0 else 0
    
    st.markdown(f"**{label}**: {current}/{total} ({percentage:.1f}%)")
    st.progress(current / total if total > 0 else 0)


# ============================================================================
# ERROR HANDLING ENHANCEMENTS
# ============================================================================

def handle_api_error(error: Exception, context: str = "operación"):
    """
    Enhanced error handling with user-friendly messages
    
    Args:
        error: Exception that occurred
        context: Context where error occurred
    """
    error_message = str(error)
    
    # Map common errors to user-friendly messages
    if "401" in error_message or "Unauthorized" in error_message:
        show_error_message(
            "Sesión expirada",
            "Por favor, inicia sesión nuevamente para continuar."
        )
    elif "403" in error_message or "Forbidden" in error_message:
        show_error_message(
            "Sin permisos",
            "No tienes permisos para realizar esta acción."
        )
    elif "404" in error_message or "Not Found" in error_message:
        show_error_message(
            "Recurso no encontrado",
            f"El elemento solicitado no existe o fue eliminado."
        )
    elif "500" in error_message or "Internal Server Error" in error_message:
        show_error_message(
            "Error del servidor",
            "Ocurrió un error interno. Por favor, intenta nuevamente más tarde."
        )
    elif "Connection" in error_message or "Network" in error_message:
        show_error_message(
            "Error de conexión",
            "No se pudo conectar con el servidor. Verifica tu conexión a internet."
        )
    else:
        show_error_message(
            f"Error en {context}",
            error_message
        )


def with_error_handling(func: callable, context: str = "operación"):
    """
    Decorator-like function to wrap operations with error handling
    
    Args:
        func: Function to execute
        context: Context description for errors
    
    Returns:
        Function result or None if error occurred
    """
    try:
        return func()
    except Exception as e:
        handle_api_error(e, context)
        return None