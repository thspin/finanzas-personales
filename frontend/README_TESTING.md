# 🧪 Frontend Testing Guide

## Resumen de Testing

Este directorio contiene una **suite completa de tests** para todos los componentes del frontend, incluyendo autenticación, formularios, API client y tablas.

## 📁 Estructura de Tests

```
frontend/tests/
├── conftest.py                    # Configuración y fixtures compartidas
├── test_components_auth.py        # Tests de autenticación JWT
├── test_components_forms.py       # Tests de formularios y validaciones  
├── test_components_api_client.py  # Tests del cliente API
├── test_components_tables.py      # Tests de tablas y visualizaciones
└── test_main.py                   # Tests de la aplicación principal
```

## 🚀 Ejecutar Tests

### Comandos Básicos

```bash
# Ejecutar todos los tests
make test

# Tests específicos por componente
make test-auth      # Tests de autenticación
make test-forms     # Tests de formularios
make test-api       # Tests de API client
make test-tables    # Tests de tablas
make test-main      # Tests de aplicación principal

# Tests con coverage
make test-coverage

# Tests verbosos
make test-verbose
```

### Comandos Avanzados

```bash
# Tests por categoría
pytest -m unit           # Solo tests unitarios
pytest -m integration    # Solo tests de integración
pytest -m auth           # Solo tests de autenticación

# Tests específicos
pytest tests/test_components_auth.py::TestRequireAuthDecorator -v
pytest tests/test_components_forms.py::TestTransactionForm -v

# Coverage detallado
pytest --cov=components --cov-report=html
```

## 📊 Coverage Objetivo

- **Mínimo requerido**: 80%
- **Objetivo**: 90%+
- **Componentes críticos**: 95%+ (auth, api_client)

## 🧩 Tests por Componente

### 1. Autenticación (`test_components_auth.py`)

**Cobertura**: Sistema completo de autenticación JWT

```python
# Tests principales
test_init_session_state()              # Inicialización de estado
test_is_authenticated()                 # Verificación de autenticación  
test_login_form_successful_login()      # Login exitoso
test_require_auth_decorator()           # Decorador de protección
test_token_management()                 # Manejo de tokens JWT
```

**Casos cubiertos**:
- ✅ Login/logout flow completo
- ✅ Validación de formularios
- ✅ Manejo de tokens JWT
- ✅ Decorador `@require_auth`
- ✅ Gestión de session state
- ✅ Errores de autenticación

### 2. Formularios (`test_components_forms.py`)

**Cobertura**: Todos los formularios de la aplicación

```python
# Tests principales  
test_transaction_form_validation()      # Validaciones de transacciones
test_credit_form_submission()           # Envío de formularios de crédito
test_service_form_auto_payment()        # Formularios de servicios
test_product_selector()                 # Selectores de productos
test_currency_selector()                # Selectores de monedas
```

**Casos cubiertos**:
- ✅ Validación en tiempo real
- ✅ Envío de formularios
- ✅ Selectores dinámicos
- ✅ Manejo de errores
- ✅ Flujos completos de creación

### 3. API Client (`test_components_api_client.py`)

**Cobertura**: Cliente API centralizado con JWT

```python
# Tests principales
test_api_client_authentication()       # Autenticación automática
test_api_client_error_handling()       # Manejo de errores HTTP
test_login_successful()                 # Login exitoso
test_handle_401_unauthorized()          # Manejo de tokens expirados
test_crud_operations()                  # Operaciones CRUD completas
```

**Casos cubiertos**:
- ✅ Autenticación JWT automática
- ✅ Manejo de errores HTTP (401, 400, 500)
- ✅ Todas las operaciones CRUD
- ✅ Gestión de tokens expirados
- ✅ Requests con/sin autenticación

### 4. Tablas (`test_components_tables.py`)

**Cobertura**: Todas las visualizaciones de datos

```python
# Tests principales
test_render_products_table()           # Tabla de productos
test_render_transactions_table()       # Tabla de transacciones
test_render_dashboard_summary()        # Resumen del dashboard
test_render_upcoming_payments()        # Próximos pagos
```

**Casos cubiertos**:
- ✅ Renderizado de tablas
- ✅ Acciones de eliminación
- ✅ Agrupación de datos
- ✅ Ordenamiento automático
- ✅ Estados vacíos

### 5. Aplicación Principal (`test_main.py`)

**Cobertura**: Flujos principales de la aplicación

```python
# Tests principales
test_main_function_renders()           # Renderizado principal
test_page_navigation()                 # Navegación entre páginas
test_dashboard_with_products()         # Dashboard con datos
test_create_product_flow()             # Flujo de creación
```

**Casos cubiertos**:
- ✅ Navegación completa
- ✅ Integración de componentes
- ✅ Flujos end-to-end
- ✅ Manejo de errores globales

## 🔧 Configuración de Tests

### Fixtures Principales (`conftest.py`)

```python
@pytest.fixture
def mock_api_client():
    """Mock del API client con datos de prueba"""
    
@pytest.fixture  
def authenticated_session_state():
    """Session state con usuario autenticado"""
    
@pytest.fixture
def mock_streamlit_components():
    """Mock de todos los componentes de Streamlit"""
```

### Marcadores de Tests

```python
pytest.mark.unit          # Tests unitarios
pytest.mark.integration   # Tests de integración
pytest.mark.auth          # Tests de autenticación
pytest.mark.forms         # Tests de formularios
pytest.mark.api           # Tests de API
pytest.mark.slow          # Tests lentos
```

## 🐛 Debugging Tests

### Modo Debug

```bash
# Debug test específico
make debug-auth
make debug-forms  
make debug-api

# Con breakpoints
pytest tests/test_components_auth.py::test_login -v -s --pdb
```

### Logs de Tests

```bash
# Ver logs detallados
pytest -v --tb=long --capture=no

# Solo failures
pytest --tb=short --no-header -q
```

## 📈 Métricas de Calidad

### Coverage Reports

```bash
# HTML report
pytest --cov=components --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=components --cov-report=term-missing
```

### Performance

```bash
# Tests más lentos
pytest --durations=10

# Solo tests rápidos  
pytest -m "not slow"
```

## 🚨 CI/CD Integration

### GitHub Actions

```yaml
- name: Run Frontend Tests
  run: |
    cd frontend
    pytest --cov=components --cov-report=xml --junitxml=junit.xml
```

### Pre-commit Hooks

```bash
# Configurar pre-commit
pip install pre-commit
pre-commit install

# Hook de tests
pytest --maxfail=1 -q
```

## 📝 Escribir Nuevos Tests

### Template para Tests

```python
"""
Tests for new_component
"""
import pytest
from unittest.mock import Mock, patch
import streamlit as st

from components.new_component import new_function


class TestNewComponent:
    """Test new component functionality"""
    
    def test_new_function_success(self, mock_streamlit_components):
        """Test successful execution of new function"""
        # Arrange
        mock_data = {"test": "data"}
        
        # Act
        result = new_function(mock_data)
        
        # Assert
        assert result is not None
        st.success.assert_called_once()
    
    def test_new_function_error(self, mock_streamlit_components):
        """Test error handling in new function"""
        # Arrange
        invalid_data = None
        
        # Act & Assert
        with pytest.raises(ValueError):
            new_function(invalid_data)


# Mark with appropriate categories
pytestmark = [
    pytest.mark.unit,
    pytest.mark.new_component
]
```

## 🔄 Continuous Testing

### Watch Mode

```bash
# Auto-rerun tests on changes
pip install pytest-watch
ptw --runner "pytest --tb=short"
```

### Integration con IDE

- **VSCode**: Python Test Explorer
- **PyCharm**: Integrated pytest runner
- **Vim/Neovim**: vim-test plugin

## 📊 Reporting

### HTML Reports

```bash
pytest --html=report.html --self-contained-html
```

### JUnit XML (para CI)

```bash
pytest --junitxml=junit.xml
```

## 🎯 Best Practices

1. **AAA Pattern**: Arrange, Act, Assert
2. **Mocking**: Mock external dependencies
3. **Fixtures**: Reutilizar setup común
4. **Parametrización**: Tests con múltiples inputs
5. **Marcadores**: Categorizar tests
6. **Coverage**: Mantener 80%+ coverage
7. **Performance**: Tests rápidos (<1s cada uno)

## 🚀 Próximos Pasos

1. **Aumentar coverage** a 95%
2. **Tests de performance** para componentes lentos
3. **Tests E2E** con Selenium
4. **Visual regression testing** para UI
5. **Property-based testing** con Hypothesis

---

**¡Los tests son fundamentales para mantener la calidad del código!** 🧪✨