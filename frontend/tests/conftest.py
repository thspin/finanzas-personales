"""
Frontend tests configuration and fixtures
"""
import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from components.api_client import FinanzasAPI
from components import auth


@pytest.fixture
def mock_api_client():
    """Mock API client for testing"""
    mock_api = Mock(spec=FinanzasAPI)
    
    # Mock common responses
    mock_api.get_currencies.return_value = [
        {"id": 1, "code": "ARS", "name": "Peso Argentino", "symbol": "$"},
        {"id": 2, "code": "USD", "name": "US Dollar", "symbol": "$"}
    ]
    
    mock_api.get_institutions.return_value = [
        {"id": 1, "name": "Banco Galicia", "logo_url": None}
    ]
    
    mock_api.get_products.return_value = [
        {
            "id": 1,
            "institution_id": 1,
            "product_type": "SAVINGS_ACCOUNT",
            "identifier": "****1234",
            "currency": {"id": 1, "code": "ARS", "symbol": "$", "name": "Peso Argentino"},
            "balance": 50000.0,
            "is_active": True,
            "institution": {"id": 1, "name": "Banco Galicia"}
        }
    ]
    
    mock_api.get_categories.return_value = [
        {"id": 1, "name": "Sueldo", "type": "INCOME", "emoji": "💰"},
        {"id": 2, "name": "Comida", "type": "EXPENSE", "emoji": "🍽️"}
    ]
    
    mock_api.get_transactions_by_product.return_value = [
        {
            "id": 1,
            "product_id": 1,
            "type": "INCOME",
            "transaction_date": "2025-01-01",
            "category": "Sueldo",
            "description": "Salario enero",
            "amount": 100000.0
        }
    ]
    
    mock_api.get_services.return_value = [
        {
            "id": 1,
            "name": "Netflix",
            "amount": 1500.0,
            "currency": {"symbol": "$", "code": "ARS"},
            "frequency": "MONTHLY",
            "next_due_date": "2025-01-15",
            "is_active": True,
            "payment_type": "AUTO"
        }
    ]
    
    mock_api.login.return_value = {
        "access_token": "fake_token_123",
        "user": {"id": 1, "username": "testuser", "email": "test@example.com"}
    }
    
    return mock_api


@pytest.fixture
def mock_session_state():
    """Mock Streamlit session state"""
    mock_state = {
        "token": None,
        "user": None,
        "logged_in": False,
        "show_notifications": False
    }
    
    with patch.object(st, 'session_state', mock_state):
        yield mock_state


@pytest.fixture
def authenticated_session_state():
    """Mock authenticated session state"""
    mock_state = {
        "token": "fake_token_123",
        "user": {"id": 1, "username": "testuser", "email": "test@example.com"},
        "logged_in": True,
        "show_notifications": False
    }
    
    with patch.object(st, 'session_state', mock_state):
        yield mock_state


@pytest.fixture
def mock_streamlit_components():
    """Mock all Streamlit components"""
    with patch.multiple(
        st,
        title=Mock(),
        header=Mock(),
        subheader=Mock(),
        write=Mock(),
        markdown=Mock(),
        text_input=Mock(),
        number_input=Mock(),
        selectbox=Mock(),
        radio=Mock(),
        checkbox=Mock(),
        date_input=Mock(),
        text_area=Mock(),
        button=Mock(return_value=False),
        form_submit_button=Mock(return_value=False),
        form=Mock(),
        columns=Mock(return_value=[Mock(), Mock()]),
        tabs=Mock(return_value=[Mock(), Mock()]),
        expander=Mock(),
        container=Mock(),
        sidebar=Mock(),
        success=Mock(),
        error=Mock(),
        warning=Mock(),
        info=Mock(),
        spinner=Mock(),
        balloons=Mock(),
        rerun=Mock(),
        divider=Mock(),
        metric=Mock(),
        dataframe=Mock(),
        set_page_config=Mock()
    ):
        # Mock st.form context manager
        mock_form = Mock()
        mock_form.__enter__ = Mock(return_value=mock_form)
        mock_form.__exit__ = Mock(return_value=None)
        st.form.return_value = mock_form
        
        # Mock st.columns to return mock columns
        col1, col2 = Mock(), Mock()
        col1.__enter__ = Mock(return_value=col1)
        col1.__exit__ = Mock(return_value=None)
        col2.__enter__ = Mock(return_value=col2)
        col2.__exit__ = Mock(return_value=None)
        st.columns.return_value = [col1, col2]
        
        # Mock st.tabs
        tab1, tab2 = Mock(), Mock()
        tab1.__enter__ = Mock(return_value=tab1)
        tab1.__exit__ = Mock(return_value=None)
        tab2.__enter__ = Mock(return_value=tab2)
        tab2.__exit__ = Mock(return_value=None)
        st.tabs.return_value = [tab1, tab2]
        
        # Mock st.expander
        mock_expander = Mock()
        mock_expander.__enter__ = Mock(return_value=mock_expander)
        mock_expander.__exit__ = Mock(return_value=None)
        st.expander.return_value = mock_expander
        
        # Mock st.container
        mock_container = Mock()
        mock_container.__enter__ = Mock(return_value=mock_container)
        mock_container.__exit__ = Mock(return_value=None)
        st.container.return_value = mock_container
        
        # Mock st.spinner
        mock_spinner = Mock()
        mock_spinner.__enter__ = Mock(return_value=mock_spinner)
        mock_spinner.__exit__ = Mock(return_value=None)
        st.spinner.return_value = mock_spinner
        
        yield


@pytest.fixture
def mock_get_api_client(mock_api_client):
    """Mock the get_api_client function"""
    with patch('components.api_client.get_api_client', return_value=mock_api_client):
        yield mock_api_client


# Common test data
@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "fake_hash"
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing"""
    return {
        "id": 1,
        "institution_id": 1,
        "product_type": "SAVINGS_ACCOUNT",
        "identifier": "****1234",
        "currency_id": 1,
        "balance": 50000.0,
        "is_active": True,
        "payment_due_day": None,
        "created_at": "2025-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing"""
    return {
        "id": 1,
        "product_id": 1,
        "type": "INCOME",
        "transaction_date": "2025-01-01",
        "category": "Sueldo",
        "description": "Salario enero",
        "amount": 100000.0,
        "created_at": "2025-01-01T00:00:00Z"
    }


# Helper functions for tests
def setup_authenticated_user(session_state, user_data=None):
    """Setup authenticated user in session state"""
    if user_data is None:
        user_data = {"id": 1, "username": "testuser", "email": "test@example.com"}
    
    session_state["token"] = "fake_token_123"
    session_state["user"] = user_data
    session_state["logged_in"] = True


def setup_unauthenticated_user(session_state):
    """Setup unauthenticated user in session state"""
    session_state["token"] = None
    session_state["user"] = None
    session_state["logged_in"] = False