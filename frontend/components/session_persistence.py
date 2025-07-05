"""
Sistema de persistencia de sesión para Streamlit
"""

import streamlit as st
import json
import os
import tempfile
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path


class SessionPersistence:
    """Maneja la persistencia de sesiones de usuario"""
    
    def __init__(self):
        # Directorio para sesiones temporales
        self.session_dir = Path(tempfile.gettempdir()) / "finanzas_sessions"
        self.session_dir.mkdir(exist_ok=True)
        
        # ID único de la sesión del navegador
        self.session_id = self._get_session_id()
        self.session_file = self.session_dir / f"session_{self.session_id}.json"
    
    def _get_session_id(self) -> str:
        """Generar ID único para la sesión del navegador"""
        # Usar el session_state de Streamlit como base
        if 'browser_session_id' not in st.session_state:
            # Crear ID único basado en timestamp y hash
            unique_data = f"{datetime.now().isoformat()}_{id(st.session_state)}"
            session_id = hashlib.md5(unique_data.encode()).hexdigest()[:16]
            st.session_state.browser_session_id = session_id
        
        return st.session_state.browser_session_id
    
    def save_session(self, token: str, user_data: dict) -> bool:
        """Guardar datos de sesión en archivo temporal"""
        try:
            session_data = {
                'token': token,
                'user': user_data,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(minutes=30)).isoformat(),
                'session_id': self.session_id
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
            
            return True
            
        except Exception as e:
            st.error(f"Error guardando sesión: {str(e)}")
            return False
    
    def load_session(self) -> Optional[Dict[str, Any]]:
        """Cargar datos de sesión desde archivo temporal"""
        try:
            if not self.session_file.exists():
                return None
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Verificar que no haya expirado
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                self.clear_session()
                return None
            
            return session_data
            
        except Exception as e:
            # Si hay error leyendo, limpiar el archivo
            self.clear_session()
            return None
    
    def clear_session(self) -> bool:
        """Eliminar archivo de sesión"""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            return True
        except Exception:
            return False
    
    def extend_session(self) -> bool:
        """Extender tiempo de expiración de sesión activa"""
        try:
            session_data = self.load_session()
            if session_data:
                session_data['expires_at'] = (datetime.now() + timedelta(minutes=30)).isoformat()
                
                with open(self.session_file, 'w') as f:
                    json.dump(session_data, f)
                
                return True
            return False
            
        except Exception:
            return False
    
    def cleanup_old_sessions(self):
        """Limpiar sesiones expiradas (llamar periódicamente)"""
        try:
            for session_file in self.session_dir.glob("session_*.json"):
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    expires_at = datetime.fromisoformat(session_data['expires_at'])
                    if datetime.now() > expires_at:
                        session_file.unlink()
                        
                except Exception:
                    # Si no se puede leer, eliminar el archivo
                    session_file.unlink()
                    
        except Exception:
            pass


# Instancia global
_session_persistence = SessionPersistence()


def save_persistent_session(token: str, user_data: dict) -> bool:
    """Guardar sesión de forma persistente"""
    return _session_persistence.save_session(token, user_data)


def load_persistent_session() -> Optional[Dict[str, Any]]:
    """Cargar sesión persistente"""
    return _session_persistence.load_session()


def clear_persistent_session() -> bool:
    """Limpiar sesión persistente"""
    return _session_persistence.clear_session()


def extend_persistent_session() -> bool:
    """Extender sesión persistente"""
    return _session_persistence.extend_session()


def init_persistent_session():
    """Inicializar sistema de persistencia y restaurar sesión si existe"""
    # Limpiar sesiones viejas
    _session_persistence.cleanup_old_sessions()
    
    # Intentar restaurar sesión existente
    if not st.session_state.get('logged_in', False):
        session_data = load_persistent_session()
        
        if session_data:
            # Verificar que el token siga siendo válido
            try:
                from .api_client import get_api_client
                
                api = get_api_client()
                api.token = session_data['token']
                api._setup_auth()
                
                # Probar el token
                current_user = api.get_current_user()
                
                if current_user:
                    # Restaurar sesión
                    st.session_state.token = session_data['token']
                    st.session_state.user = session_data['user']
                    st.session_state.logged_in = True
                    
                    # Extender tiempo de sesión
                    extend_persistent_session()
                    
                    return True
                else:
                    # Token inválido, limpiar
                    clear_persistent_session()
                    
            except Exception:
                # Error con el token, limpiar
                clear_persistent_session()
    
    return False