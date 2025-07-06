import streamlit as st
import os
import json

def load_page_state():
    """Cargar estado de página desde archivo temporal"""
    try:
        temp_file = f"/tmp/finanzas_page_state_{os.environ.get('USER', 'default')}.json"
        if os.path.exists(temp_file):
            with open(temp_file, 'r') as f:
                data = json.load(f)
                return data.get('current_page', 'dashboard')
    except:
        pass
    return 'dashboard'

def save_page_state(page):
    """Guardar estado de página en archivo temporal"""
    try:
        temp_file = f"/tmp/finanzas_page_state_{os.environ.get('USER', 'default')}.json"
        with open(temp_file, 'w') as f:
            json.dump({'current_page': page}, f)
    except:
        pass

def simple_navigation():
    """Navegación simplificada y robusta con persistencia"""
    
    # Inicializar página actual con persistencia
    if 'current_page' not in st.session_state:
        # Intentar cargar desde archivo temporal
        saved_page = load_page_state()
        st.session_state.current_page = saved_page
    
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
                # Guardar estado de página
                save_page_state(page_key)
                st.rerun()
    
    # Guardar estado actual al final (para persistencia en refresh)
    save_page_state(st.session_state.current_page)
    
    return st.session_state.current_page

# Función para reemplazar la navegación actual
def get_simple_navigation():
    """Obtener navegación simple"""
    return simple_navigation()