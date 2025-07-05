import requests
import streamlit as st
from typing import Dict, List, Optional, Any
import json


class FinanzasAPI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self._setup_auth()
    
    def _setup_auth(self):
        """Configure authentication headers if token exists"""
        if 'token' in st.session_state and st.session_state.token:
            self.session.headers.update({
                'Authorization': f'Bearer {st.session_state.token}'
            })
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response with error checking"""
        if response.status_code == 401:
            st.session_state.token = None
            st.session_state.user = None
            st.error("Sesión expirada. Por favor, inicia sesión nuevamente.")
            st.rerun()
        
        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', f'Error {response.status_code}')
            except:
                error_msg = f'Error {response.status_code}: {response.text}'
            raise Exception(error_msg)
        
        return response.json()
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        return self._handle_response(response)
    
    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data)
        return self._handle_response(response)
    
    def _put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.put(url, json=data)
        return self._handle_response(response)
    
    def _delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.delete(url)
        return self._handle_response(response)
    
    # Authentication methods
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user and get token"""
        data = {'username': username, 'password': password}
        response = self.session.post(f"{self.base_url}/auth/login", data=data)
        return self._handle_response(response)
    
    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register new user"""
        data = {'username': username, 'email': email, 'password': password}
        return self._post("/auth/register", data)
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user info"""
        return self._get("/auth/me")
    
    # Currency methods
    def get_currencies(self) -> List[Dict[str, Any]]:
        """Get all currencies"""
        return self._get("/currencies/")
    
    def create_currency(self, currency_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new currency"""
        return self._post("/currencies/", currency_data)
    
    # Institution methods
    def get_institutions(self) -> List[Dict[str, Any]]:
        """Get user's institutions"""
        return self._get("/institutions/")
    
    def create_institution(self, institution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new institution"""
        return self._post("/institutions/", institution_data)
    
    def delete_institution(self, institution_id: int) -> Dict[str, Any]:
        """Delete institution"""
        return self._delete(f"/institutions/{institution_id}")
    
    # Product methods
    def get_products(self) -> List[Dict[str, Any]]:
        """Get user's products"""
        return self._get("/products/")
    
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new product"""
        return self._post("/products/", product_data)
    
    def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Delete product"""
        return self._delete(f"/products/{product_id}")
    
    # Transaction methods
    def create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new transaction"""
        return self._post("/transactions/", transaction_data)
    
    def get_transactions_by_product(self, product_id: int) -> List[Dict[str, Any]]:
        """Get transactions for a product"""
        return self._get(f"/transactions/product/{product_id}")
    
    # Credit methods
    def create_credit(self, credit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new credit"""
        return self._post("/credits/", credit_data)
    
    def get_credits_by_product(self, product_id: int) -> List[Dict[str, Any]]:
        """Get credits for a product"""
        return self._get(f"/credits/product/{product_id}")
    
    def get_credit_installments(self, credit_id: int) -> List[Dict[str, Any]]:
        """Get installments for a credit"""
        return self._get(f"/credits/{credit_id}/installments")
    
    # Category methods
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get user's categories"""
        return self._get("/categories/")
    
    def create_category(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new category"""
        return self._post("/categories/", category_data)
    
    def delete_category(self, category_id: int) -> Dict[str, Any]:
        """Delete category"""
        return self._delete(f"/categories/{category_id}")
    
    def initialize_default_categories(self) -> Dict[str, Any]:
        """Initialize default categories"""
        return self._post("/categories/initialize-defaults")
    
    # Service methods
    def get_services(self) -> List[Dict[str, Any]]:
        """Get user's services"""
        return self._get("/services/")
    
    def create_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new service"""
        return self._post("/services/", service_data)
    
    def delete_service(self, service_id: int) -> Dict[str, Any]:
        """Delete service"""
        return self._delete(f"/services/{service_id}")
    
    def get_upcoming_services(self) -> List[Dict[str, Any]]:
        """Get upcoming services"""
        return self._get("/services/upcoming")
    
    # Notification methods
    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get user's notifications"""
        return self._get("/notifications/")
    
    def get_notification_count(self) -> Dict[str, Any]:
        """Get unread notification count"""
        return self._get("/notifications/count")
    
    def mark_notification_read(self, notification_id: int) -> Dict[str, Any]:
        """Mark notification as read"""
        return self._put(f"/notifications/{notification_id}/read")
    
    def mark_all_notifications_read(self) -> Dict[str, Any]:
        """Mark all notifications as read"""
        return self._put("/notifications/read-all")
    
    def delete_notification(self, notification_id: int) -> Dict[str, Any]:
        """Delete notification"""
        return self._delete(f"/notifications/{notification_id}")


# Global API client instance
@st.cache_resource
def get_api_client():
    """Get cached API client instance"""
    return FinanzasAPI()