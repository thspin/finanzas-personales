#!/usr/bin/env python3
"""
Script para solucionar problemas comunes del sistema de finanzas personales
"""

import sys
import os
import subprocess
import requests
import time

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def check_services():
    """Verificar estado de los servicios"""
    print("🔍 Verificando servicios...")
    
    # Verificar backend
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print("✅ Backend: Funcionando correctamente")
            else:
                print(f"⚠️ Backend: Estado {data.get('status')}")
                print(f"   Base de datos: {data.get('database')}")
        else:
            print(f"❌ Backend: Error HTTP {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ Backend: No responde en http://localhost:8000")
    
    # Verificar frontend
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: Funcionando correctamente")
        else:
            print(f"❌ Frontend: Error HTTP {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ Frontend: No responde en http://localhost:8501")

def test_authentication():
    """Probar autenticación con usuario de prueba"""
    print("\n🔐 Probando autenticación...")
    
    try:
        # Probar login
        login_data = {
            "username": "testuser",
            "password": "test123"
        }
        
        response = requests.post(
            "http://localhost:8000/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login exitoso")
            print(f"   Usuario: {data['user']['username']}")
            print(f"   Email: {data['user']['email']}")
            
            # Probar endpoint protegido
            token = data["access_token"]
            auth_headers = {"Authorization": f"Bearer {token}"}
            
            profile_response = requests.get(
                "http://localhost:8000/auth/me",
                headers=auth_headers,
                timeout=5
            )
            
            if profile_response.status_code == 200:
                print("✅ Endpoints protegidos: Funcionando")
            else:
                print("❌ Endpoints protegidos: Error")
                
        else:
            print(f"❌ Login falló: HTTP {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")

def create_user_if_needed():
    """Crear usuario de prueba si no existe"""
    print("\n👤 Verificando usuario de prueba...")
    
    try:
        # Intentar login primero
        login_data = {
            "username": "testuser",
            "password": "test123"
        }
        
        response = requests.post(
            "http://localhost:8000/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Usuario de prueba ya existe y funciona")
            return True
        else:
            print("⚠️ Usuario de prueba no funciona, recreando...")
            
            # Ejecutar script de creación
            result = subprocess.run([
                sys.executable, 
                "create_test_user.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Usuario de prueba recreado")
                return True
            else:
                print(f"❌ Error al crear usuario: {result.stderr}")
                return False
                
    except requests.exceptions.RequestException:
        print("❌ No se puede conectar al backend para verificar usuario")
        return False

def show_access_info():
    """Mostrar información de acceso"""
    print("\n" + "="*60)
    print("📋 INFORMACIÓN DE ACCESO")
    print("="*60)
    print("🌐 Frontend: http://localhost:8501")
    print("🔧 API Backend: http://localhost:8000")
    print("📚 Documentación API: http://localhost:8000/docs")
    print()
    print("👤 Usuario de Prueba:")
    print("   📧 Email: test@finanzas.com")
    print("   👤 Username: testuser")
    print("   🔑 Password: test123")
    print()
    print("💡 Si tienes problemas:")
    print("   1. Ejecuta: python fix_common_issues.py")
    print("   2. Verifica que PostgreSQL esté ejecutándose")
    print("   3. Reinicia los servicios con: ./start.sh")

def main():
    """Función principal"""
    print("🔧 SOLUCIONADOR DE PROBLEMAS - Finanzas Personales")
    print("="*60)
    
    # Verificar servicios
    check_services()
    
    # Verificar y crear usuario si es necesario
    user_ok = create_user_if_needed()
    
    # Probar autenticación
    if user_ok:
        test_authentication()
    
    # Mostrar información de acceso
    show_access_info()
    
    print("\n✨ Diagnóstico completado!")

if __name__ == "__main__":
    main()