# 🤝 Guía de Contribución - Finanzas Personales

¡Gracias por tu interés en contribuir a este proyecto! Esta guía te ayudará a entender cómo puedes participar y colaborar efectivamente.

## 📋 Tabla de Contenidos

- [Cómo Contribuir](#cómo-contribuir)
- [Configuración del Entorno](#configuración-del-entorno)
- [Estándares de Código](#estándares-de-código)
- [Proceso de Testing](#proceso-de-testing)
- [Envío de Cambios](#envío-de-cambios)
- [Reporte de Bugs](#reporte-de-bugs)
- [Solicitar Nuevas Funcionalidades](#solicitar-nuevas-funcionalidades)

## 🚀 Cómo Contribuir

### Tipos de Contribuciones

1. **🐛 Reportar Bugs**: Encuentra y reporta errores
2. **✨ Nuevas Funcionalidades**: Propón mejoras o características nuevas
3. **📚 Documentación**: Mejora la documentación existente
4. **🧪 Testing**: Agrega o mejora tests
5. **🎨 UX/UI**: Mejoras en la experiencia de usuario
6. **⚡ Performance**: Optimizaciones de rendimiento

### Primeros Pasos

1. **Fork** el repositorio
2. **Clone** tu fork localmente
3. **Configura** el entorno de desarrollo
4. **Crea** una rama para tu contribución
5. **Desarrolla** tu mejora
6. **Testea** tus cambios
7. **Envía** un Pull Request

## ⚙️ Configuración del Entorno

### Requisitos Previos

- Python 3.12+
- PostgreSQL 16+
- Git
- Editor de código (recomendado: VS Code)

### Setup Rápido

```bash
# 1. Fork y clone el repositorio
git clone https://github.com/TU_USUARIO/finanzas-personales.git
cd finanzas-personales

# 2. Configurar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos
cp .env.example .env
# Editar .env con tus configuraciones

# 5. Crear base de datos
sudo -u postgres psql
CREATE USER finanzas_user WITH PASSWORD 'finanzas_pass';
CREATE DATABASE finanzas_db OWNER finanzas_user;
CREATE DATABASE finanzas_test_db OWNER finanzas_user;
\q

# 6. Inicializar esquema
cd backend
python -c "from app.database import engine; from app import models; models.Base.metadata.create_all(bind=engine)"

# 7. Ejecutar tests para verificar
cd ../frontend && make test
cd ../backend && pytest
```

### Configuración del Editor

#### VS Code (Recomendado)

Instala estas extensiones:
- Python
- Pylance
- Python Docstring Generator
- GitLens
- Thunder Client (para testing API)

Configuración recomendada (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

## 📏 Estándares de Código

### Python Style Guide

Seguimos **PEP 8** con algunas adaptaciones:

#### Formato General
```python
# ✅ Correcto
def calculate_monthly_payment(amount: float, rate: float, months: int) -> float:
    """
    Calculate monthly payment for a loan.
    
    Args:
        amount: Principal loan amount
        rate: Monthly interest rate (as decimal)
        months: Number of months
    
    Returns:
        Monthly payment amount
    """
    if months <= 0:
        raise ValueError("Months must be positive")
    
    return amount * (rate * (1 + rate)**months) / ((1 + rate)**months - 1)
```

#### Imports
```python
# ✅ Orden correcto de imports
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.models import User, Transaction
from app.schemas import UserCreate, TransactionResponse
```

#### Naming Conventions
- **Variables y funciones**: `snake_case`
- **Clases**: `PascalCase`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Archivos**: `snake_case.py`

#### Docstrings
Usa formato Google:
```python
def process_transaction(transaction_data: dict, user_id: int) -> Transaction:
    """
    Process a new financial transaction.
    
    Args:
        transaction_data: Dictionary containing transaction details
        user_id: ID of the user creating the transaction
    
    Returns:
        Created transaction object
    
    Raises:
        ValueError: If transaction data is invalid
        AuthenticationError: If user is not authorized
    """
```

### Frontend (Streamlit)

#### Componentes
```python
# ✅ Estructura de componente
def render_transaction_form(
    products: List[Dict[str, Any]], 
    categories: List[Dict[str, Any]]
) -> None:
    """
    Render transaction creation form with validation.
    
    Args:
        products: Available financial products
        categories: Available transaction categories
    """
    with st.form("transaction_form"):
        # Form content here
        pass
```

#### UX Guidelines
- **Feedback inmediato**: Usa loading spinners y mensajes de estado
- **Validación en tiempo real**: Valida mientras el usuario escribe
- **Mensajes claros**: Errores específicos y actionables
- **Navegación intuitiva**: Breadcrumbs y navegación consistente

## 🧪 Proceso de Testing

### Tests Obligatorios

Toda contribución debe incluir tests apropiados:

#### Backend Tests
```bash
cd backend

# Ejecutar todos los tests
pytest

# Tests específicos
pytest tests/test_auth.py -v
pytest tests/test_transactions.py::test_create_transaction -v

# Con coverage
pytest --cov=app tests/ --cov-report=html
```

#### Frontend Tests
```bash
cd frontend

# Ejecutar todos los tests
make test

# Tests específicos
make test-auth
make test-forms

# Con coverage
make test-coverage
```

### Escribir Nuevos Tests

#### Test Backend
```python
def test_create_transaction_success(client, auth_headers, sample_product):
    """Test successful transaction creation."""
    transaction_data = {
        "product_id": sample_product.id,
        "type": "INCOME",
        "amount": 1500.00,
        "category": "Salary",
        "description": "Monthly salary"
    }
    
    response = client.post(
        "/transactions/",
        json=transaction_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 1500.00
    assert data["type"] == "INCOME"
```

#### Test Frontend
```python
def test_transaction_form_validation(mock_streamlit_components):
    """Test transaction form validation."""
    products = [{"id": 1, "name": "Test Account"}]
    categories = [{"id": 1, "name": "Salary", "type": "INCOME"}]
    
    transaction_form(products, [], categories)
    
    # Verify validation messages appear
    mock_streamlit_components.warning.assert_called_with(
        "No hay monedas disponibles"
    )
```

### Coverage Requirements

- **Backend**: Mínimo 80% coverage
- **Frontend**: Mínimo 75% coverage
- **Componentes críticos**: 90%+ coverage (auth, transactions, payments)

## 📨 Envío de Cambios

### Git Workflow

```bash
# 1. Crear rama para tu feature
git checkout -b feature/descripcion-corta

# 2. Hacer commits descriptivos
git add .
git commit -m "feat: add real-time validation to transaction forms

- Implement validate_amount_real_time function
- Add visual feedback for form validation
- Include duplicate transaction detection
- Update tests for new validation logic

Fixes #123"

# 3. Push a tu fork
git push origin feature/descripcion-corta

# 4. Crear Pull Request
```

### Commits Convencionales

Usa [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Tipos de commit
feat: nueva funcionalidad
fix: corrección de bug
docs: solo documentación
style: formato, espacios, etc.
refactor: refactoring sin cambios funcionales
test: agregar o corregir tests
chore: tareas de mantenimiento
```

**Ejemplos:**
```bash
feat: add password strength validation to registration form
fix: resolve JWT token expiration handling
docs: update API documentation for transactions endpoint
test: add integration tests for credit management
refactor: extract common validation logic to utils
```

### Pull Request Guidelines

#### Título del PR
```
feat: implement real-time form validation for better UX
```

#### Descripción del PR
```markdown
## 📝 Descripción

Implementa validación en tiempo real para todos los formularios de la aplicación, mejorando significativamente la experiencia de usuario.

## 🎯 Cambios Realizados

- ✅ Validación en tiempo real para campos de monto
- ✅ Detección automática de transacciones duplicadas
- ✅ Feedback visual inmediato para errores
- ✅ Mejoras en la navegación con breadcrumbs
- ✅ Tests completos para nuevas funcionalidades

## 🧪 Testing

- [x] Todos los tests existentes pasan
- [x] Nuevos tests agregados con 85% coverage
- [x] Tests manuales en Chrome y Firefox
- [x] Validación en dispositivos móviles

## 📸 Screenshots

[Agregar capturas de pantalla si aplica]

## 🔗 Issues Relacionados

Closes #123
Related to #124

## 📋 Checklist

- [x] El código sigue los estándares del proyecto
- [x] Tests agregados/actualizados
- [x] Documentación actualizada
- [x] Sin warnings de linting
- [x] Coverage mínimo cumplido
```

### Review Checklist

Antes de enviar tu PR, verifica:

- [ ] **Código**: Sigue los estándares establecidos
- [ ] **Tests**: Todos pasan y coverage es adecuado
- [ ] **Documentación**: Actualizada si es necesario
- [ ] **Performance**: No introduce ralentizaciones
- [ ] **Security**: No introduce vulnerabilidades
- [ ] **UX**: Mejora la experiencia de usuario
- [ ] **Backward Compatibility**: No rompe funcionalidad existente

## 🐛 Reporte de Bugs

### Template de Bug Report

```markdown
**🐛 Descripción del Bug**
Descripción clara y concisa del problema.

**🔄 Pasos para Reproducir**
1. Ve a '...'
2. Haz clic en '....'
3. Scroll down to '....'
4. Ver error

**✅ Comportamiento Esperado**
Descripción clara de lo que esperabas que pasara.

**❌ Comportamiento Actual**
Descripción clara de lo que realmente pasa.

**📸 Screenshots**
Si aplica, agrega screenshots para explicar el problema.

**🖥️ Entorno:**
 - OS: [e.g. Ubuntu 24.04, Windows 11]
 - Browser [e.g. chrome, safari]
 - Python Version [e.g. 3.12.0]
 - Version [e.g. 1.2.0]

**📝 Información Adicional**
Cualquier otro contexto sobre el problema.

**🔍 Logs**
```
[Pegar logs relevantes aquí]
```
```

## ✨ Solicitar Nuevas Funcionalidades

### Template de Feature Request

```markdown
**🚀 Descripción de la Funcionalidad**
Descripción clara y concisa de lo que quieres que se agregue.

**💡 Problema que Resuelve**
¿Qué problema específico resolvería esta funcionalidad?

**💭 Solución Propuesta**
Descripción clara de lo que te gustaría que pasara.

**🔄 Alternativas Consideradas**
Descripción de cualquier solución alternativa que hayas considerado.

**📊 Impacto en Usuarios**
¿Cómo beneficiaría esta funcionalidad a los usuarios?

**⚙️ Complejidad Técnica**
¿Tienes alguna idea sobre la complejidad de implementación?

**📱 Mockups/Wireframes**
Si aplica, agrega diseños o mockups.

**📝 Información Adicional**
Cualquier otro contexto o screenshots sobre la funcionalidad.
```

## 🏷️ Labels y Categorización

### Labels de Issues
- `bug` - Reportes de errores
- `enhancement` - Nuevas funcionalidades
- `documentation` - Mejoras en documentación
- `good first issue` - Bueno para principiantes
- `help wanted` - Se busca ayuda externa
- `priority: high` - Alta prioridad
- `priority: medium` - Prioridad media
- `priority: low` - Baja prioridad
- `area: backend` - Relacionado con FastAPI
- `area: frontend` - Relacionado con Streamlit
- `area: database` - Relacionado con PostgreSQL
- `area: testing` - Relacionado con tests
- `area: ux` - Experiencia de usuario

### Labels de PRs
- `feature` - Nueva funcionalidad
- `bugfix` - Corrección de bug
- `refactor` - Refactoring
- `docs` - Solo documentación
- `tests` - Solo tests
- `breaking change` - Cambios que rompen compatibilidad

## 🤝 Código de Conducta

### Nuestros Estándares

- **Sé respetuoso**: Trata a todos con respeto y profesionalismo
- **Sé constructivo**: Proporciona feedback constructivo y específico
- **Sé paciente**: No todos tienen el mismo nivel de experiencia
- **Sé inclusivo**: Fomenta un ambiente acogedor para todos

### Comportamientos No Aceptados

- Lenguaje o imágenes sexualizadas
- Trolling, comentarios insultantes/despectivos
- Acoso público o privado
- Publicar información privada de otros
- Cualquier comportamiento considerado inapropiado profesionalmente

## 📞 Contacto y Soporte

### Canales de Comunicación

- **Issues**: Para bugs y feature requests
- **Discussions**: Para preguntas y discusiones generales
- **Email**: [email de contacto si aplica]

### Tiempo de Respuesta

- **Issues**: 2-3 días hábiles
- **Pull Requests**: 3-5 días hábiles
- **Security Issues**: 24 horas

## 🎉 Reconocimientos

### Contributors

Agradecemos a todos los que contribuyen a este proyecto. Los contribuidores serán reconocidos en:

- README.md
- Releases notes
- Contributors page

### Hall of Fame

Los mejores contribuidores podrán obtener:
- Menciones especiales
- Acceso temprano a nuevas funcionalidades
- Rol de maintainer (para contribuidores frecuentes)

---

**¡Gracias por contribuir a Finanzas Personales! 🚀**

Tu participación hace que este proyecto sea mejor para todos. Si tienes preguntas sobre esta guía, no dudes en abrir un issue de discusión.