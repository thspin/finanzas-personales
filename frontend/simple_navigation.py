import streamlit as st

def simple_navigation():
    """Navegación simplificada y robusta"""
    
    # Inicializar página actual si no existe
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Opciones del menú
    menu_options = {
        "🏠 Dashboard": "dashboard",
        "🏦 Productos": "products", 
        "💰 Transacciones": "transactions",
        "🏧 Créditos": "credits",
        "📋 Servicios": "services",
        "⚙️ Configuración": "config",
        "📊 Reportes": "reports"
    }
    
    st.sidebar.title("📊 Panel de Control")
    
    # Mostrar página actual
    current_display = None
    for display_name, page_key in menu_options.items():
        if page_key == st.session_state.current_page:
            current_display = display_name
            break
    
    st.sidebar.info(f"Página actual: {current_display}")
    
    # Menú de navegación
    st.sidebar.markdown("### 🧭 Navegar a:")
    
    for display_name, page_key in menu_options.items():
        # Indicar página activa
        if page_key == st.session_state.current_page:
            st.sidebar.markdown(f"**▶ {display_name}** (actual)")
        else:
            if st.sidebar.button(display_name, key=f"nav_{page_key}"):
                st.session_state.current_page = page_key
                st.rerun()
    
    return st.session_state.current_page

# Función para reemplazar la navegación actual
def get_simple_navigation():
    """Obtener navegación simple"""
    return simple_navigation()