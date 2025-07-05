import streamlit as st
from .api_client import get_api_client
from .session_persistence import (
    save_persistent_session, 
    clear_persistent_session, 
    init_persistent_session
)
from typing import Optional, Dict, Any


# Las funciones de persistencia ahora están en session_persistence.py


def init_session_state():
    """Initialize session state variables with persistence support"""
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Try to restore session from persistent storage
    session_restored = init_persistent_session()
    
    if session_restored:
        st.rerun()


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('logged_in', False) and st.session_state.get('token') is not None


def logout():
    """Logout user and clear session with persistence"""
    # Clear session state
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.logged_in = False
    
    # Clear persistent storage
    clear_persistent_session()
    
    st.success("Sesión cerrada exitosamente")
    st.rerun()


def login_form():
    """Render login form with tabs for login and register"""
    st.title("🏦 Finanzas Personales")
    
    # Use tabs to separate login and register
    tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "🆕 Registrarse"])
    
    with tab1:
        show_login_tab()
    
    with tab2:
        show_register_tab()


def show_login_tab():
    """Show login tab"""
    st.subheader("Iniciar Sesión")
    
    api = get_api_client()
    
    with st.form("login_form"):
        username = st.text_input("Usuario o Email")
        password = st.text_input("Contraseña", type="password")
        
        login_submitted = st.form_submit_button("Iniciar Sesión", type="primary")
    
    if login_submitted and username and password:
        try:
            with st.spinner("Iniciando sesión..."):
                response = api.login(username, password)
                
                # Save to session state
                st.session_state.token = response['access_token']
                st.session_state.user = response['user']
                st.session_state.logged_in = True
                
                # Update API client with new token
                api._setup_auth()
                
                # Save session persistently
                save_persistent_session(response['access_token'], response['user'])
                
                st.success(f"¡Bienvenido, {response['user']['username']}!")
                st.rerun()
                
        except Exception as e:
            st.error(f"Error al iniciar sesión: {str(e)}")
    elif login_submitted:
        st.error("Por favor completa todos los campos")


def show_register_tab():
    """Show register tab"""
    st.subheader("Crear Nueva Cuenta")
    
    api = get_api_client()
    
    with st.form("register_form"):
        username = st.text_input("Nombre de Usuario")
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")
        confirm_password = st.text_input("Confirmar Contraseña", type="password")
        
        register_submitted = st.form_submit_button("Crear Cuenta", type="primary")
    
    if register_submitted:
        if not all([username, email, password, confirm_password]):
            st.error("Todos los campos son obligatorios")
            return
        
        if password != confirm_password:
            st.error("Las contraseñas no coinciden")
            return
        
        if len(password) < 6:
            st.error("La contraseña debe tener al menos 6 caracteres")
            return
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            st.error("Por favor ingresa un email válido")
            return
        
        try:
            with st.spinner("Creando cuenta..."):
                response = api.register(username, email, password)
                st.success("¡Cuenta creada exitosamente! Ahora puedes iniciar sesión en la pestaña anterior.")
                
        except Exception as e:
            error_msg = str(e)
            if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                st.error("El usuario o email ya existe. Intenta con otros datos.")
            else:
                st.error(f"Error al crear cuenta: {error_msg}")


# La función register_form ahora está integrada en show_register_tab()


def require_auth(func):
    """Decorator to require authentication for a function"""
    def wrapper(*args, **kwargs):
        init_session_state()
        
        if not is_authenticated():
            login_form()
            return
        
        return func(*args, **kwargs)
    
    return wrapper


def render_user_info():
    """Render user info in sidebar with session persistence info"""
    if is_authenticated() and st.session_state.user:
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"**👤 {st.session_state.user['username']}**")
            st.markdown(f"📧 {st.session_state.user['email']}")
            
            # Show session info
            with st.expander("🔒 Sesión"):
                st.success("✅ Activa")
                st.info("💾 Persistente")
                st.caption("⏰ 30 min de duración")
            
            if st.button("🚪 Cerrar Sesión", type="secondary"):
                logout()


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current authenticated user"""
    if is_authenticated():
        return st.session_state.user
    return None