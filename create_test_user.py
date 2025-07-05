#!/usr/bin/env python3
"""
Script para crear un usuario de prueba en el sistema de finanzas personales
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.database import SessionLocal, engine
from backend.app.models import User, Institution, Product, Currency
from backend.app.schemas import UserCreate
from backend.app.auth import get_password_hash
from sqlalchemy.orm import Session
from sqlalchemy import text

def create_test_user():
    """Crear usuario de prueba con datos iniciales"""
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        print("🔧 Creando usuario de prueba...")
        
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(User.email == "test@finanzas.com").first()
        if existing_user:
            print("✅ Usuario de prueba ya existe:")
            print(f"   📧 Email: test@finanzas.com")
            print(f"   👤 Username: testuser")
            print(f"   🔑 Password: test123")
            return
        
        # Crear usuario de prueba
        hashed_password = get_password_hash("test123")
        test_user = User(
            username="testuser",
            email="test@finanzas.com",
            hashed_password=hashed_password
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✅ Usuario de prueba creado exitosamente!")
        print(f"   📧 Email: test@finanzas.com")
        print(f"   👤 Username: testuser")
        print(f"   🔑 Password: test123")
        print(f"   🆔 User ID: {test_user.id}")
        
        # Verificar que existan monedas básicas
        currencies = db.query(Currency).all()
        if not currencies:
            print("\n🪙 Creando monedas básicas...")
            
            basic_currencies = [
                Currency(code="USD", name="Dólar Estadounidense", symbol="$"),
                Currency(code="EUR", name="Euro", symbol="€"),
                Currency(code="ARS", name="Peso Argentino", symbol="$"),
                Currency(code="CLP", name="Peso Chileno", symbol="$"),
                Currency(code="MXN", name="Peso Mexicano", symbol="$"),
                Currency(code="COP", name="Peso Colombiano", symbol="$"),
            ]
            
            for currency in basic_currencies:
                db.add(currency)
            
            db.commit()
            print("✅ Monedas básicas creadas")
        
        # Crear institución de ejemplo
        print("\n🏦 Creando institución de ejemplo...")
        
        usd_currency = db.query(Currency).filter(Currency.code == "USD").first()
        
        test_institution = Institution(
            user_id=test_user.id,
            name="Banco Ejemplo",
            logo_url="https://via.placeholder.com/100x50?text=BANCO"
        )
        
        db.add(test_institution)
        db.commit()
        db.refresh(test_institution)
        
        print(f"✅ Institución creada: {test_institution.name}")
        
        # Crear producto de ejemplo
        print("\n💳 Creando producto de ejemplo...")
        
        test_product = Product(
            user_id=test_user.id,
            institution_id=test_institution.id,
            product_type="CHECKING_ACCOUNT",
            identifier="****1234",
            currency_id=usd_currency.id,
            balance=1000.00,
            payment_due_day=15,
            is_active=True
        )
        
        db.add(test_product)
        db.commit()
        db.refresh(test_product)
        
        print(f"✅ Producto creado: {test_product.product_type} - {test_product.identifier}")
        print(f"   💰 Saldo inicial: ${test_product.balance}")
        
        print("\n🎉 ¡Setup completo!")
        print("\n📋 Datos para iniciar sesión:")
        print("   🌐 Frontend: http://localhost:8501")
        print("   📧 Email: test@finanzas.com")
        print("   👤 Username: testuser")
        print("   🔑 Password: test123")
        
    except Exception as e:
        print(f"❌ Error al crear usuario de prueba: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_database_connection():
    """Verificar conexión a base de datos"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Conexión a base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Script de creación de usuario de prueba")
    print("=" * 50)
    
    # Verificar conexión
    if not verify_database_connection():
        print("\n💡 Sugerencias:")
        print("   1. Verificar que PostgreSQL esté ejecutándose")
        print("   2. Verificar variables de entorno en .env")
        print("   3. Verificar permisos de base de datos")
        sys.exit(1)
    
    # Crear usuario de prueba
    create_test_user()
    
    print("\n" + "=" * 50)
    print("✨ Ahora puedes iniciar sesión en la aplicación!")