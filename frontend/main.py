import streamlit as st
from datetime import date, datetime
from typing import List, Dict, Any

# Import custom components
from components.auth import require_auth, render_user_info, init_session_state
from components.api_client import get_api_client
from components.forms import (
    transaction_form, credit_form, service_form, 
    product_selector, institution_selector_or_create,
    notification_bell, render_notifications_sidebar
)
from components.tables import (
    render_products_table, render_transactions_table, 
    render_credits_table, render_services_table,
    render_categories_table, render_currencies_table,
    render_dashboard_summary, render_upcoming_payments
)
from components.ui_helpers import (
    render_breadcrumbs, sidebar_navigation_enhanced, quick_actions_sidebar,
    search_functionality, show_loading_spinner, show_error_message,
    show_success_message, show_warning_message, handle_api_error,
    with_error_handling
)
from simple_navigation import get_simple_navigation
from components.performance import (
    get_dashboard_data, get_transactions_cached, get_master_data,
    render_transactions_paginated, progressive_data_loading,
    lazy_load_component, clear_performance_cache, performance_monitor
)

# Page configuration
st.set_page_config(
    page_title="💰 Finanzas Personales",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


@require_auth
def main():
    """Main application function with enhanced UX"""
    # Render user info in sidebar
    render_user_info()
    
    # Render notifications sidebar if needed
    render_notifications_sidebar()
    
    # Header with notification bell
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<h1 class="main-header">💰 Sistema de Finanzas Personales</h1>', unsafe_allow_html=True)
    with col2:
        notification_bell()
    
    # Enhanced navigation sidebar
    menu_options = {
        "🏠 Dashboard": "dashboard",
        "🏦 Gestionar Productos": "products", 
        "💰 Transacciones": "transactions",
        "🏧 Créditos": "credits",
        "📋 Servicios": "services",
        "⚙️ Configuración": "config",
        "📊 Reportes": "reports"
    }
    
    # Get notification count for enhanced navigation
    try:
        api = get_api_client()
        notification_count = api.get_notification_count().get('unread_count', 0)
    except:
        notification_count = 0
    
    # Get current page from session state or default
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Simple and robust navigation
    page = get_simple_navigation()
    
    # Handle quick actions (simplified)
    if st.session_state.get('quick_action'):
        if st.session_state.quick_action == "transaction":
            st.session_state.current_page = "transactions"
        elif st.session_state.quick_action == "credit":
            st.session_state.current_page = "credits"
        # Guardar estado de página
        from simple_navigation import save_page_state
        save_page_state(st.session_state.current_page)
        # Clear quick action
        del st.session_state.quick_action
        st.rerun()
    
    # Quick actions in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Acciones Rápidas")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.sidebar.button("💰 Nueva Transacción", key="quick_trans"):
            st.session_state.current_page = "transactions"
            from simple_navigation import save_page_state
            save_page_state("transactions")
            st.rerun()
    with col2:
        if st.sidebar.button("🏧 Nuevo Crédito", key="quick_cred"):
            st.session_state.current_page = "credits"
            from simple_navigation import save_page_state
            save_page_state("credits")
            st.rerun()
    
    # Show breadcrumbs
    page_hierarchy = []
    page_names = {
        "dashboard": "Dashboard",
        "products": "Gestionar Productos",
        "transactions": "Transacciones",
        "credits": "Créditos",
        "services": "Servicios",
        "config": "Configuración",
        "reports": "Reportes"
    }
    
    render_breadcrumbs(page_names.get(page, "Página"), page_hierarchy)
    
    # Show selected page with enhanced error handling
    try:
        if page == "dashboard":
            show_dashboard()
        elif page == "products":
            show_products_page()
        elif page == "transactions":
            show_transactions_page()
        elif page == "credits":
            show_credits_page()
        elif page == "services":
            show_services_page()
        elif page == "config":
            show_config_page()
        elif page == "reports":
            show_reports_page()
        else:
            st.error(f"Página '{page}' no encontrada")
            st.info("Redirigiendo al dashboard...")
            st.session_state.current_page = "dashboard"
            st.rerun()
    except Exception as e:
        st.error(f"❗ Error en la página {page_names.get(page, page)}")
        st.error(f"Detalles: {str(e)}")
        
        # Mostrar botón para volver al dashboard
        if st.button("← Volver al Dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        # Mostrar detalles del error en expander
        with st.expander("🔍 Ver detalles técnicos"):
            st.code(str(e))
            import traceback
            st.code(traceback.format_exc())


@performance_monitor
def show_dashboard():
    """Show enhanced main dashboard with performance optimizations"""
    st.header("🏠 Dashboard")
    
    # Add cache controls in sidebar
    with st.sidebar.expander("🚀 Performance"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧹 Limpiar Cache"):
                clear_performance_cache()
        with col2:
            cache_info = st.session_state.get('cache_info', {})
            st.metric("Cache Hits", len(cache_info))
    
    # Get user token for caching
    user_token = st.session_state.get('token', '')
    
    # Use cached dashboard data
    dashboard_data = get_dashboard_data(user_token)
    
    if not dashboard_data:
        show_error_message("No se pudieron cargar los datos del dashboard")
        return
    
    products = dashboard_data.get('products', [])
    services = dashboard_data.get('services', [])
    institutions = dashboard_data.get('institutions', [])
    currencies = dashboard_data.get('currencies', [])
    metrics = dashboard_data.get('metrics', {})
    
    if products:
        # Show cached data timestamp
        loaded_at = dashboard_data.get('loaded_at', '')
        if loaded_at:
            try:
                from datetime import datetime
                load_time = datetime.fromisoformat(loaded_at)
                st.caption(f"🔄 Última actualización: {load_time.strftime('%H:%M:%S')}")
            except:
                pass
        
        # Enhanced dashboard summary with metrics
        st.subheader("📊 Resumen Financiero")
        
        # Display metrics from cache
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Productos Activos", metrics.get('active_products', 0))
        with col2:
            st.metric("Servicios Activos", metrics.get('active_services', 0))
        with col3:
            st.metric("Monedas en Uso", metrics.get('currencies_in_use', 0))
        with col4:
            st.metric("Pagos Próximos", metrics.get('upcoming_payments', 0))
        
        # Balance by currency from cached metrics
        if metrics.get('balance_by_currency'):
            st.subheader("💰 Saldos por Moneda")
            balance_cols = st.columns(len(metrics['balance_by_currency']))
            for i, (currency, data) in enumerate(metrics['balance_by_currency'].items()):
                with balance_cols[i]:
                    st.metric(
                        f"{data['symbol']} {currency}",
                        f"{data['symbol']} {data['total']:,.2f}",
                        help=f"{data['products_count']} productos"
                    )
        
        st.markdown("---")
        
        # Products overview with enhanced search
        st.subheader("💳 Resumen de Productos")
        
        # Add search functionality for large datasets
        if len(products) > 5:
            filtered_products = search_functionality(
                products, 
                ['product_type', 'identifier', 'institution']
            )
        else:
            filtered_products = products
        
        render_products_table(filtered_products, institutions)
        
        st.markdown("---")
        
        # Recent activity with lazy loading
        st.subheader("📈 Actividad Reciente")
        
        def load_recent_activity():
            from components.performance import load_recent_activity
            return load_recent_activity(user_token, limit=10)
        
        recent_activities = lazy_load_component(
            "recent_activity",
            load_recent_activity,
            "Cargando actividad reciente...",
            "Error al cargar actividad reciente"
        )
        
        if recent_activities:
            # Display recent activities in a compact format
            for activity in recent_activities[:5]:  # Show only 5 most recent
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"💰 {activity.get('description', 'Transacción')}")
                    with col2:
                        amount = activity.get('amount', 0)
                        st.write(f"${amount:,.2f}")
                    with col3:
                        date_str = activity.get('transaction_date', '')
                        st.write(date_str[:10] if date_str else '')
        
        # Upcoming payments
        if services:
            render_upcoming_payments(services)
        else:
            st.info("💡 No hay servicios registrados. Ve a la sección Servicios para agregar suscripciones.")
            
    else:
        st.info("👋 ¡Bienvenido! No tienes productos registrados aún. Comienza creando un producto financiero.")
        
        # Quick start actions
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🏦 Crear Primer Producto", use_container_width=True):
                st.session_state.current_page = "products"
                st.rerun()
        
        with col2:
            if st.button("📚 Ver Guía de Inicio", use_container_width=True):
                st.info("💡 **Guía rápida:**\n1. Crea un producto financiero (cuenta, tarjeta)\n2. Agrega transacciones\n3. Configura servicios recurrentes\n4. Revisa tu dashboard")


def show_products_page():
    """Page to manage financial products"""
    # Manejar rerun después de crear producto
    if st.session_state.get('should_rerun', False):
        st.session_state.should_rerun = False
        st.rerun()
        
    # Manejar flag de producto creado
    if st.session_state.get('product_created', False):
        st.session_state.product_created = False
        st.balloons()
        st.success("🎉 ¡Producto creado! Actualiza la página o cambia de tab para ver el nuevo producto.")
    
    st.header("🏦 Gestionar Productos Financieros")
    st.write("Administra tus productos financieros: cuentas de ahorro, corrientes, tarjetas de crédito, etc.")
    
    # Tabs for creating and viewing products
    tab1, tab2 = st.tabs(["➕ Crear Producto", "📋 Ver Productos"])
    
    with tab1:
        show_create_product_form()
    
    with tab2:
        show_products_list()


def show_create_product_form():
    """Form to create new financial product - SIMPLIFIED FOR DEBUGGING"""
    st.subheader("➕ Crear Nuevo Producto Financiero")
    
    # DEBUG: Mostrar información de depuración
    st.info("🔍 **Modo DEBUG activado** - Formulario simplificado para diagnosticar problemas")
    
    api = get_api_client()
    
    try:
        # Load required data
        with st.spinner("Cargando datos..."):
            currencies = api.get_currencies()
            institutions = api.get_institutions()
        
        st.success(f"✅ Datos cargados: {len(institutions)} instituciones, {len(currencies)} monedas")
        
        # DEBUG: Mostrar datos cargados
        with st.expander("🔍 Ver datos cargados (DEBUG)"):
            st.write("**Instituciones:**", institutions)
            st.write("**Monedas:**", currencies)
        
        # Mostrar mensaje si no hay instituciones
        if not institutions:
            st.warning("⚠️ No hay instituciones. Crea una primero.")
            with st.form("create_institution_form"):
                st.markdown("#### Crear Institución")
                inst_name = st.text_input("Nombre", placeholder="Ej: Banco Galicia")
                inst_logo = st.text_input("Logo URL (opcional)")
                
                if st.form_submit_button("Crear Institución"):
                    if inst_name.strip():
                        try:
                            result = api.create_institution({
                                "name": inst_name.strip(), 
                                "logo_url": inst_logo.strip() if inst_logo else None
                            })
                            st.success(f"✅ Institución creada: {result}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error creando institución: {str(e)}")
                    else:
                        st.error("❌ Nombre requerido")
            return
        
        # Formulario principal - SIMPLIFICADO
        with st.form("simple_product_form"):
            st.markdown("#### Datos del Producto")
            
            # Selección de institución simple
            institution_names = [inst['name'] for inst in institutions]
            selected_inst_name = st.selectbox("🏛️ Institución", institution_names)
            selected_institution = next(inst for inst in institutions if inst['name'] == selected_inst_name)
            
            # Tipo de producto
            product_types = {
                "CHECKING_ACCOUNT": "Cuenta Corriente",
                "SAVINGS_ACCOUNT": "Caja de Ahorro", 
                "CREDIT_CARD": "Tarjeta de Crédito",
                "INVESTMENT": "Inversión",
                "LOAN": "Préstamo"
            }
            selected_type = st.selectbox("📝 Tipo", list(product_types.keys()), format_func=lambda x: product_types[x])
            
            # Identificador
            identifier = st.text_input("🔢 Identificador", placeholder="****1234")
            
            # Moneda simple
            currency_names = [f"{curr['code']} - {curr['name']}" for curr in currencies]
            selected_curr_name = st.selectbox("💱 Moneda", currency_names)
            selected_currency = next(curr for curr in currencies if f"{curr['code']} - {curr['name']}" == selected_curr_name)
            
            # Día de vencimiento
            payment_day = st.number_input("📅 Día Vencimiento", 1, 31, 15)
            
            # Submit
            submitted = st.form_submit_button("✅ CREAR PRODUCTO", use_container_width=True)
            
            # DEBUG: Mostrar datos del formulario
            if st.form_submit_button("🔍 Ver datos (DEBUG)"):
                st.write("**Datos del formulario:**")
                st.json({
                    "institution_id": selected_institution['id'],
                    "product_type": selected_type,
                    "identifier": identifier,
                    "currency_id": selected_currency['id'],
                    "payment_due_day": payment_day if selected_type == "CREDIT_CARD" else None
                })
        
        # Procesar formulario FUERA del with form
        if submitted:
            st.info("🔄 Procesando formulario...")
            
            if not identifier.strip():
                st.error("❌ Identificador requerido")
                return
                
            product_data = {
                "institution_id": selected_institution['id'],
                "product_type": selected_type,
                "identifier": identifier.strip(),
                "currency_id": selected_currency['id'],
                "payment_due_day": payment_day if selected_type == "CREDIT_CARD" else None
            }
            
            st.write("🔍 **Datos a enviar:**", product_data)
            
            try:
                with st.spinner("Creando producto..."):
                    result = api.create_product(product_data)
                
                st.success("✅ ¡Producto creado exitosamente!")
                st.json(result)
                
                # Limpiar cache y marcar para reload
                from components.performance import clear_performance_cache
                clear_performance_cache()
                st.session_state.product_created = True
                
            except Exception as e:
                st.error(f"❌ Error creando producto: {str(e)}")
                st.exception(e)
                    
    except Exception as e:
        st.error(f"❌ Error cargando datos: {str(e)}")
        st.exception(e)


def show_products_list():
    """List existing financial products"""
    st.subheader("📋 Productos Registrados")
    
    api = get_api_client()
    
    try:
        products = api.get_products()
        institutions = api.get_institutions()
        
        if products:
            render_products_table(products, institutions)
        else:
            st.info("📝 No hay productos registrados aún")
            
    except Exception as e:
        handle_api_error(e, "cargar productos")


def show_transactions_page():
    """Enhanced page for managing transactions with performance optimizations"""
    st.header("💰 Gestión de Transacciones")
    
    import time
    start_time = time.time()
    
    # Performance metrics in sidebar
    with st.sidebar.expander("📈 Métricas de Performance"):
        load_time = time.time() - start_time
        st.metric("Tiempo de Carga", f"{load_time:.2f}s")
    
    # Tabs for different transaction actions (MOVED OUTSIDE SIDEBAR)
    tab1, tab2, tab3 = st.tabs(["➕ Nueva Transacción", "📋 Ver Transacciones", "📈 Análisis"])
    
    with tab1:
        show_transaction_form()
    
    with tab2:
        show_transactions_list()
    
    with tab3:
        show_transaction_analysis()


def show_transaction_analysis():
    """Show transaction analysis with cached data"""
    st.subheader("📈 Análisis de Transacciones")
    
    user_token = st.session_state.get('token', '')
    
    # Progressive data loading for analysis
    data_loaders = [
        ("Productos", lambda: get_api_client().get_products()),
        ("Transacciones", lambda: get_transactions_cached([p['id'] for p in get_api_client().get_products()], 500)),
        ("Categorías", lambda: get_api_client().get_categories())
    ]
    
    loaded_data = progressive_data_loading(data_loaders, show_progress=True)
    
    if all(data['data'] for data in loaded_data.values() if data.get('data') is not None):
        transactions = loaded_data['Transacciones']['data']
        categories = loaded_data['Categorías']['data']
        
        if transactions:
            import pandas as pd
            from datetime import datetime, timedelta
            
            # Create DataFrame for analysis
            df_data = []
            for trans in transactions:
                df_data.append({
                    'fecha': trans.get('transaction_date', ''),
                    'tipo': trans.get('type', ''),
                    'categoria': trans.get('category', ''),
                    'monto': trans.get('amount', 0)
                })
            
            df = pd.DataFrame(df_data)
            
            if not df.empty:
                # Convert date column
                df['fecha'] = pd.to_datetime(df['fecha'])
                
                # Analysis metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Por Categoría")
                    category_summary = df.groupby('categoria')['monto'].sum().sort_values(ascending=False)
                    st.bar_chart(category_summary)
                
                with col2:
                    st.subheader("📅 Por Mes")
                    df['mes'] = df['fecha'].dt.to_period('M')
                    monthly_summary = df.groupby(['mes', 'tipo'])['monto'].sum().unstack(fill_value=0)
                    if not monthly_summary.empty:
                        st.line_chart(monthly_summary)
                
                # Recent trends
                st.subheader("📈 Tendencias Recientes (30 días)")
                recent_date = datetime.now() - timedelta(days=30)
                recent_df = df[df['fecha'] >= recent_date]
                
                if not recent_df.empty:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        recent_income = recent_df[recent_df['tipo'] == 'INCOME']['monto'].sum()
                        st.metric("Ingresos (30d)", f"${recent_income:,.2f}")
                    
                    with col2:
                        recent_expense = recent_df[recent_df['tipo'] == 'EXPENSE']['monto'].sum()
                        st.metric("Egresos (30d)", f"${recent_expense:,.2f}")
                    
                    with col3:
                        net_balance = recent_income - recent_expense
                        st.metric("Balance Neto (30d)", f"${net_balance:,.2f}")
                else:
                    st.info("No hay transacciones en los últimos 30 días")
        else:
            st.info("No hay transacciones para analizar")
    else:
        st.error("No se pudieron cargar los datos para el análisis")


def show_transaction_form():
    """Show enhanced transaction creation form"""
    api = get_api_client()
    
    def load_transaction_data():
        """Load all required data for transactions"""
        with show_loading_spinner("Cargando datos..."):
            products = api.get_products()
            currencies = api.get_currencies()
            categories = api.get_categories()
            return products, currencies, categories
    
    # Load data with error handling
    data = with_error_handling(load_transaction_data, "cargar datos para transacciones")
    
    if not data:
        return
    
    products, currencies, categories = data
    
    if not products:
        show_warning_message("Primero debes crear al menos un producto financiero")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("🏦 Crear Producto"):
                st.session_state.current_page = "products"
                st.rerun()
        return
    
    if not categories:
        show_warning_message("No hay categorías disponibles")
        st.info("💡 Ve a Configuración → Categorías para crear algunas")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("⚙️ Ir a Configuración"):
                st.session_state.current_page = "config"
                st.rerun()
        return
    
    # Render enhanced transaction form component
    transaction_form(products, currencies, categories)


@performance_monitor
def show_transactions_list():
    """List recent transactions with pagination and performance optimizations"""
    st.subheader("📋 Transacciones")
    
    api = get_api_client()
    user_token = st.session_state.get('token', '')
    
    # Load products for transaction filtering
    master_data = get_master_data(user_token)
    products = master_data.get('data', {}).get('products', [])
    
    if not products:
        st.warning("No hay productos disponibles para mostrar transacciones")
        return
    
    # Get product IDs for cached transaction loading
    product_ids = [p['id'] for p in products if p.get('is_active', True)]
    
    # Add filter controls
    with st.expander("🔍 Filtros Avanzados"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_product = st.selectbox(
                "Filtrar por Producto",
                ["Todos"] + [f"{p.get('institution', {}).get('name', '')} - {p.get('product_type', '')}" for p in products],
                key="transaction_filter_product"
            )
        
        with col2:
            transaction_type_filter = st.selectbox(
                "Tipo de Transacción",
                ["Todos", "Ingresos", "Egresos"],
                key="transaction_filter_type"
            )
        
        with col3:
            limit_transactions = st.number_input(
                "Límite de Transacciones",
                min_value=10,
                max_value=1000,
                value=100,
                step=10,
                key="transaction_limit"
            )
    
    # Filter product IDs based on selection
    if selected_product != "Todos":
        # Find the selected product
        for i, product in enumerate(products):
            product_display = f"{product.get('institution', {}).get('name', '')} - {product.get('product_type', '')}"
            if product_display == selected_product:
                product_ids = [product['id']]
                break
    
    # Load transactions with caching
    try:
        all_transactions = get_transactions_cached(product_ids, limit_transactions)
        
        # Apply type filter
        if transaction_type_filter == "Ingresos":
            all_transactions = [t for t in all_transactions if t.get('type') == 'INCOME']
        elif transaction_type_filter == "Egresos":
            all_transactions = [t for t in all_transactions if t.get('type') == 'EXPENSE']
        
        if all_transactions:
            # Show transaction summary
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Transacciones", len(all_transactions))
            
            with col2:
                income_count = len([t for t in all_transactions if t.get('type') == 'INCOME'])
                st.metric("Ingresos", income_count)
            
            with col3:
                expense_count = len([t for t in all_transactions if t.get('type') == 'EXPENSE'])
                st.metric("Egresos", expense_count)
            
            with col4:
                total_amount = sum(t.get('amount', 0) for t in all_transactions if t.get('type') == 'INCOME') - \
                              sum(t.get('amount', 0) for t in all_transactions if t.get('type') == 'EXPENSE')
                st.metric("Balance Neto", f"${total_amount:,.2f}")
            
            st.markdown("---")
            
            # Add search functionality for large datasets
            if len(all_transactions) > 10:
                filtered_transactions = search_functionality(
                    all_transactions,
                    ['description', 'category', 'type', 'amount']
                )
            else:
                filtered_transactions = all_transactions
            
            # Use paginated rendering for better performance
            render_transactions_paginated(
                filtered_transactions,
                key="main_transactions",
                items_per_page=20
            )
            
        else:
            st.info("📝 No hay transacciones que coincidan con los filtros")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("💰 Crear Primera Transacción"):
                    st.session_state.transaction_tab = 0
                    st.rerun()
    
    except Exception as e:
        handle_api_error(e, "cargar transacciones")
    
    try:
        # Get products and transactions
        products = api.get_products()
        
        if not products:
            st.info("📝 No hay productos registrados")
            return
        
        # Get all transactions
        all_transactions = []
        for product in products:
            try:
                transactions = api.get_transactions_by_product(product['id'])
                for trans in transactions:
                    trans['product_name'] = f"{product['institution']['name']} - {product['product_type']}"
                    all_transactions.append(trans)
            except:
                continue
        
        if all_transactions:
            render_transactions_table(all_transactions)
        else:
            st.info("📝 No hay transacciones registradas aún")
            
    except Exception as e:
        st.error(f"❌ Error al cargar transacciones: {str(e)}")


def show_credits_page():
    """Page for managing credits"""
    st.header("🏧 Gestión de Créditos")
    
    # Tabs for credit management
    tab1, tab2 = st.tabs(["💳 Nuevo Crédito", "📋 Ver Créditos y Cuotas"])
    
    with tab1:
        show_credit_form_page()
    
    with tab2:
        show_credits_list()


def show_credit_form_page():
    """Show credit creation form"""
    api = get_api_client()
    
    try:
        # Load products (only credit cards)
        products = api.get_products()
        
        if not products:
            st.warning("⚠️ Primero debes crear al menos un producto financiero")
            return
        
        # Render credit form component
        credit_form(products)
        
    except Exception as e:
        st.error(f"❌ Error al cargar datos para créditos: {str(e)}")


def show_credits_list():
    """List credits and installments"""
    st.subheader("📋 Créditos y Cuotas")
    
    api = get_api_client()
    
    try:
        # Get products (filter credit cards)
        products = api.get_products()
        credit_products = [p for p in products if p['product_type'] == 'CREDIT_CARD']
        
        if not credit_products:
            st.info("📝 No hay tarjetas de crédito registradas")
            return
        
        # Get all credits
        all_credits = []
        for product in credit_products:
            try:
                credits = api.get_credits_by_product(product['id'])
                for credit in credits:
                    credit['product_name'] = f"{product['institution']['name']} - {product['product_type']}"
                    all_credits.append(credit)
            except:
                continue
        
        if all_credits:
            render_credits_table(all_credits)
        else:
            st.info("📝 No hay créditos registrados aún")
            
    except Exception as e:
        st.error(f"❌ Error al cargar créditos: {str(e)}")


def show_services_page():
    """Page for managing services and subscriptions"""
    st.header("📋 Servicios y Suscripciones")
    st.write("Gestiona tus servicios, suscripciones y pagos recurrentes para nunca olvidar un vencimiento.")
    
    # Tabs for different functions
    tab1, tab2, tab3 = st.tabs(["➕ Nuevo Servicio", "📋 Mis Servicios", "📅 Próximos Pagos"])
    
    with tab1:
        show_service_form_page()
    
    with tab2:
        show_services_list()
    
    with tab3:
        show_upcoming_services()


def show_service_form_page():
    """Show service creation form"""
    api = get_api_client()
    
    try:
        # Load required data
        products = api.get_products()
        currencies = api.get_currencies()
        
        # Render service form component
        service_form(products, currencies)
        
    except Exception as e:
        st.error(f"❌ Error al cargar datos para servicios: {str(e)}")


def show_services_list():
    """List existing services"""
    st.subheader("📋 Mis Servicios")
    
    api = get_api_client()
    
    try:
        services = api.get_services()
        
        if services:
            render_services_table(services)
        else:
            st.info("📝 No hay servicios registrados aún")
            st.write("💡 **Tip:** Agrega tus servicios y suscripciones para nunca olvidar un pago")
            
    except Exception as e:
        st.error(f"❌ Error al cargar servicios: {str(e)}")


def show_upcoming_services():
    """Show upcoming service payments"""
    st.subheader("📅 Próximos Pagos")
    
    api = get_api_client()
    
    try:
        services = api.get_services()
        
        if services:
            render_upcoming_payments(services)
        else:
            st.info("📅 No hay servicios próximos a vencer")
            
    except Exception as e:
        st.error(f"❌ Error al cargar servicios próximos: {str(e)}")


def show_config_page():
    """System configuration page"""
    st.header("⚙️ Configuración")
    st.write("Configura categorías y otros aspectos del sistema de finanzas.")
    
    # Configuration tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📂 Categorías", "💱 Monedas", "🏦 Instituciones", "🔧 Preferencias"])
    
    with tab1:
        show_categories_management()
    
    with tab2:
        show_currencies_management()
    
    with tab3:
        show_institutions_management()
    
    with tab4:
        show_preferences()


def show_currencies_management():
    """Currency management"""
    st.subheader("💱 Gestión de Monedas")
    st.write("Administra las monedas disponibles en el sistema (fiat, cripto, etc.)")
    
    api = get_api_client()
    
    try:
        currencies = api.get_currencies()
        
        # Show current currencies
        st.write("**Monedas disponibles:**")
        render_currencies_table(currencies)
        
        st.divider()
        
        # Add new currency form
        st.write("**Agregar nueva moneda:**")
        with st.form("add_currency"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_code = st.text_input("Código (2-4 caracteres)", placeholder="USDT", max_chars=4).upper()
            with col2:
                new_name = st.text_input("Nombre completo", placeholder="Bitcoin")
            with col3:
                new_symbol = st.text_input("Símbolo", placeholder="₿", max_chars=5)
            
            submitted = st.form_submit_button("➕ Agregar Moneda")
            
            if submitted and new_code and new_name and new_symbol:
                # Validate code doesn't exist
                existing_codes = [curr['code'] for curr in currencies]
                if new_code in existing_codes:
                    st.error(f"❌ Ya existe una moneda con código {new_code}")
                elif len(new_code) < 2:
                    st.error("❌ El código debe tener al menos 2 caracteres")
                else:
                    try:
                        currency_data = {
                            "code": new_code,
                            "name": new_name,
                            "symbol": new_symbol
                        }
                        with st.spinner("Creando moneda..."):
                            api.create_currency(currency_data)
                        
                        st.success(f"✅ Moneda {new_symbol} {new_code} - {new_name} agregada exitosamente!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error al crear moneda: {str(e)}")
                        
    except Exception as e:
        st.error(f"❌ Error al cargar monedas: {str(e)}")


def show_categories_management():
    """Category management"""
    st.subheader("📂 Gestión de Categorías")
    
    api = get_api_client()
    
    try:
        categories = api.get_categories()
        
        # Show current categories
        render_categories_table(categories)
        
        st.divider()
        
        # Add new category form
        st.write("**Agregar nueva categoría:**")
        with st.form("add_category"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                category_name = st.text_input("Nombre", placeholder="Ej: Comida")
            
            with col2:
                category_type = st.selectbox("Tipo", ["INCOME", "EXPENSE"], 
                                           format_func=lambda x: "Ingreso" if x == "INCOME" else "Egreso")
            
            with col3:
                emoji_options = ["💰", "💻", "📈", "🛒", "🎁", "🎉", "💵", "🏠", "💼", "🍽️", "🚗", "💡", "🎬", "🏥"]
                selected_emoji = st.selectbox("Emoji", emoji_options, index=0)
            
            submitted = st.form_submit_button("➕ Agregar Categoría")
            
            if submitted and category_name:
                try:
                    category_data = {
                        "name": category_name,
                        "type": category_type,
                        "emoji": selected_emoji
                    }
                    
                    with st.spinner("Creando categoría..."):
                        api.create_category(category_data)
                    
                    st.success(f"✅ Categoría '{category_name}' creada exitosamente!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al crear categoría: {str(e)}")
        
        # Initialize default categories button
        if st.button("🔄 Inicializar Categorías por Defecto"):
            try:
                with st.spinner("Inicializando categorías..."):
                    api.initialize_default_categories()
                st.success("✅ Categorías por defecto inicializadas!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al inicializar categorías: {str(e)}")
                
    except Exception as e:
        st.error(f"❌ Error al cargar categorías: {str(e)}")


def show_institutions_management():
    """Institution management"""
    st.subheader("🏦 Gestión de Instituciones")
    st.write("Administra las instituciones financieras (bancos, fintech, etc.)")
    
    api = get_api_client()
    
    try:
        institutions = api.get_institutions()
        
        # Show current institutions
        st.write("**Instituciones disponibles:**")
        
        if institutions:
            # Display institutions in a nice format
            for institution in institutions:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.write(f"**🏦 {institution['name']}**")
                        if institution.get('logo_url'):
                            st.caption(f"Logo: {institution['logo_url']}")
                    
                    with col2:
                        st.caption(f"ID: {institution['id']}")
                        if 'created_at' in institution:
                            st.caption(f"Creada: {institution['created_at'][:10]}")
                    
                    with col3:
                        if st.button("🗑️", key=f"delete_inst_{institution['id']}", help="Eliminar institución"):
                            try:
                                # Note: Need to implement delete endpoint in API
                                st.warning("Función de eliminar pendiente de implementar")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
                    st.divider()
        else:
            st.info("No hay instituciones creadas aún")
        
        st.divider()
        
        # Add new institution form
        st.write("**Agregar nueva institución:**")
        with st.form("add_institution"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input(
                    "Nombre de la institución", 
                    placeholder="Ej: Banco Galicia",
                    help="Nombre completo de la institución financiera"
                )
            
            with col2:
                new_logo_url = st.text_input(
                    "URL del logo (opcional)", 
                    placeholder="https://ejemplo.com/logo.png",
                    help="URL de la imagen del logo"
                )
            
            submitted = st.form_submit_button("➕ Agregar Institución")
            
            if submitted and new_name:
                # Validate name doesn't exist
                existing_names = [inst['name'] for inst in institutions]
                if new_name in existing_names:
                    st.error(f"❌ Ya existe una institución con el nombre '{new_name}'")
                else:
                    try:
                        institution_data = {
                            "name": new_name,
                            "logo_url": new_logo_url if new_logo_url else None
                        }
                        with st.spinner("Creando institución..."):
                            result = api.create_institution(institution_data)
                        
                        st.success(f"✅ Institución '{new_name}' agregada exitosamente!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error al crear institución: {str(e)}")
            elif submitted:
                st.error("❌ El nombre de la institución es obligatorio")
                        
    except Exception as e:
        st.error(f"Error al cargar instituciones: {str(e)}")
        st.info("💡 Asegúrate de estar logueado correctamente")


def show_preferences():
    """General preferences"""
    st.subheader("🔧 Preferencias Generales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Moneda por defecto:**")
        default_currency = st.selectbox("Seleccionar moneda", ["ARS", "USD", "EUR"], index=0)
        
        st.write("**Formato de fecha:**")
        date_format = st.selectbox("Formato", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"], index=0)
    
    with col2:
        st.write("**Configuraciones de notificaciones:**")
        notify_due_dates = st.checkbox("Notificar fechas de vencimiento", value=True)
        notify_low_balance = st.checkbox("Notificar saldo bajo", value=False)
        
        if notify_low_balance:
            min_balance = st.number_input("Saldo mínimo para notificar", min_value=0.0, value=1000.0)
    
    if st.button("💾 Guardar Preferencias"):
        st.success("✅ Preferencias guardadas (próximamente persistente)")


def show_reports_page():
    """Reports page"""
    st.header("📊 Reportes")
    st.write("Próximamente: Gráficos y análisis avanzados")
    
    # Placeholder for future charts and analytics
    st.info("🚧 Esta sección estará disponible en futuras versiones con gráficos interactivos")


if __name__ == "__main__":
    main()