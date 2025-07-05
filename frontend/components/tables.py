import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from .api_client import get_api_client


def render_products_table(products: List[Dict[str, Any]], institutions: List[Dict[str, Any]]):
    """
    Render products table grouped by institution
    """
    if not products:
        st.info("No hay productos registrados")
        return
    
    api = get_api_client()
    
    # Group by institution
    institutions_dict = {inst['id']: inst for inst in institutions}
    
    for institution in institutions:
        inst_products = [p for p in products if p['institution_id'] == institution['id']]
        
        if not inst_products:
            continue
        
        st.subheader(f"🏛️ {institution['name']}")
        
        # Create DataFrame for this institution
        data = []
        for product in inst_products:
            data.append({
                'Tipo': product['product_type'],
                'Identificador': product.get('identifier', 'N/A'),
                'Moneda': product['currency']['code'],
                'Saldo': f"{product['currency']['symbol']} {product['balance']:,.2f}",
                'Estado': '✅ Activo' if product['is_active'] else '❌ Inactivo',
                'ID': product['id']
            })
        
        df = pd.DataFrame(data)
        
        # Display table
        st.dataframe(
            df[['Tipo', 'Identificador', 'Moneda', 'Saldo', 'Estado']], 
            use_container_width=True,
            hide_index=True
        )
        
        # Delete buttons
        with st.expander(f"Gestionar productos de {institution['name']}"):
            for i, product in enumerate(inst_products):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"{product['product_type']} ({product.get('identifier', 'N/A')})")
                
                with col2:
                    if st.button(
                        "🗑️ Eliminar", 
                        key=f"delete_product_{product['id']}",
                        type="secondary"
                    ):
                        try:
                            api.delete_product(product['id'])
                            st.success("Producto eliminado")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        st.markdown("---")


def render_transactions_table(transactions: List[Dict[str, Any]]):
    """
    Render transactions table
    """
    if not transactions:
        st.info("No hay transacciones registradas")
        return
    
    # Create DataFrame
    data = []
    for trans in transactions:
        data.append({
            'Fecha': trans['transaction_date'],
            'Tipo': '💰 Ingreso' if trans['type'] == 'INCOME' else '💸 Egreso',
            'Categoría': trans['category'],
            'Descripción': trans.get('description', ''),
            'Monto': f"{trans['amount']:,.2f}",
            'ID': trans['id']
        })
    
    df = pd.DataFrame(data)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df = df.sort_values('Fecha', ascending=False)
    
    st.dataframe(
        df[['Fecha', 'Tipo', 'Categoría', 'Descripción', 'Monto']], 
        use_container_width=True,
        hide_index=True
    )


def render_credits_table(credits: List[Dict[str, Any]]):
    """
    Render credits table with installments
    """
    if not credits:
        st.info("No hay créditos registrados")
        return
    
    api = get_api_client()
    
    for credit in credits:
        st.subheader(f"💳 {credit['description']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Monto Total", f"${credit['total_amount']:,.2f}")
        
        with col2:
            st.metric("Cuotas Totales", credit['total_installments'])
        
        with col3:
            st.metric("Fecha Compra", credit['purchase_date'])
        
        # Get installments
        try:
            installments = api.get_credit_installments(credit['id'])
            
            if installments:
                # Create installments DataFrame
                inst_data = []
                for inst in installments:
                    status_emoji = '✅' if inst['status'] == 'PAID' else '⏳'
                    inst_data.append({
                        'Cuota': inst['installment_number'],
                        'Monto': f"${inst['amount']:,.2f}",
                        'Vencimiento': inst['due_date'],
                        'Estado': f"{status_emoji} {inst['status']}"
                    })
                
                df = pd.DataFrame(inst_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"Error al cargar cuotas: {str(e)}")
        
        st.markdown("---")


def render_services_table(services: List[Dict[str, Any]]):
    """
    Render services table
    """
    if not services:
        st.info("No hay servicios/suscripciones registrados")
        return
    
    api = get_api_client()
    
    # Create DataFrame
    data = []
    for service in services:
        payment_info = ""
        if service['payment_type'] == 'AUTO' and service.get('product'):
            payment_info = f"Auto desde {service['product']['product_type']}"
        else:
            payment_info = "Manual"
        
        data.append({
            'Servicio': service['name'],
            'Monto': f"{service['currency']['symbol']} {service['amount']:,.2f}",
            'Frecuencia': service['frequency'],
            'Próximo Pago': service['next_due_date'],
            'Tipo Pago': payment_info,
            'Estado': '✅ Activo' if service['is_active'] else '❌ Inactivo',
            'ID': service['id']
        })
    
    df = pd.DataFrame(data)
    df['Próximo Pago'] = pd.to_datetime(df['Próximo Pago'])
    df = df.sort_values('Próximo Pago')
    
    st.dataframe(
        df[['Servicio', 'Monto', 'Frecuencia', 'Próximo Pago', 'Tipo Pago', 'Estado']], 
        use_container_width=True,
        hide_index=True
    )
    
    # Delete buttons in expander
    with st.expander("Gestionar servicios"):
        for service in services:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"{service['name']} - {service['currency']['symbol']} {service['amount']:,.2f}")
            
            with col2:
                if st.button(
                    "🗑️ Eliminar", 
                    key=f"delete_service_{service['id']}",
                    type="secondary"
                ):
                    try:
                        api.delete_service(service['id'])
                        st.success("Servicio eliminado")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")


def render_categories_table(categories: List[Dict[str, Any]]):
    """
    Render categories table
    """
    if not categories:
        st.info("No hay categorías registradas")
        return
    
    api = get_api_client()
    
    # Separate by type
    income_cats = [c for c in categories if c['type'] == 'INCOME']
    expense_cats = [c for c in categories if c['type'] == 'EXPENSE']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Categorías de Ingresos")
        if income_cats:
            for cat in income_cats:
                col_emoji, col_name, col_delete = st.columns([1, 3, 1])
                
                with col_emoji:
                    st.write(cat['emoji'])
                
                with col_name:
                    st.write(cat['name'])
                
                with col_delete:
                    if st.button("🗑️", key=f"delete_income_cat_{cat['id']}"):
                        try:
                            api.delete_category(cat['id'])
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        else:
            st.info("No hay categorías de ingresos")
    
    with col2:
        st.subheader("💸 Categorías de Egresos")
        if expense_cats:
            for cat in expense_cats:
                col_emoji, col_name, col_delete = st.columns([1, 3, 1])
                
                with col_emoji:
                    st.write(cat['emoji'])
                
                with col_name:
                    st.write(cat['name'])
                
                with col_delete:
                    if st.button("🗑️", key=f"delete_expense_cat_{cat['id']}"):
                        try:
                            api.delete_category(cat['id'])
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        else:
            st.info("No hay categorías de egresos")


def render_currencies_table(currencies: List[Dict[str, Any]]):
    """
    Render currencies table
    """
    if not currencies:
        st.info("No hay monedas registradas")
        return
    
    # Create DataFrame
    data = []
    for currency in currencies:
        data.append({
            'Código': currency['code'],
            'Nombre': currency['name'],
            'Símbolo': currency['symbol'],
            'ID': currency['id']
        })
    
    df = pd.DataFrame(data)
    
    st.dataframe(
        df[['Código', 'Nombre', 'Símbolo']], 
        use_container_width=True,
        hide_index=True
    )


def render_dashboard_summary(
    products: List[Dict[str, Any]], 
    currencies: List[Dict[str, Any]]
):
    """
    Render dashboard summary cards
    """
    # Calculate balances by currency
    balances_by_currency = {}
    
    for product in products:
        if not product['is_active']:
            continue
            
        currency_code = product['currency']['code']
        currency_symbol = product['currency']['symbol']
        
        if currency_code not in balances_by_currency:
            balances_by_currency[currency_code] = {
                'symbol': currency_symbol,
                'total': 0,
                'products_count': 0
            }
        
        balances_by_currency[currency_code]['total'] += float(product['balance'])
        balances_by_currency[currency_code]['products_count'] += 1
    
    if not balances_by_currency:
        st.info("No hay productos activos para mostrar resumen")
        return
    
    # Display summary cards
    cols = st.columns(len(balances_by_currency))
    
    for i, (currency_code, data) in enumerate(balances_by_currency.items()):
        with cols[i]:
            st.metric(
                label=f"Total {currency_code}",
                value=f"{data['symbol']} {data['total']:,.2f}",
                help=f"{data['products_count']} productos activos"
            )


def render_upcoming_payments(services: List[Dict[str, Any]]):
    """
    Render upcoming payments widget
    """
    from datetime import date, timedelta
    
    # Filter services due in next 30 days
    today = date.today()
    upcoming_date = today + timedelta(days=30)
    
    upcoming = []
    for service in services:
        if not service['is_active']:
            continue
            
        due_date = datetime.strptime(service['next_due_date'], '%Y-%m-%d').date()
        if today <= due_date <= upcoming_date:
            upcoming.append({
                'name': service['name'],
                'amount': service['amount'],
                'currency': service['currency']['symbol'],
                'due_date': due_date,
                'days_left': (due_date - today).days
            })
    
    if not upcoming:
        st.info("No hay pagos próximos en los próximos 30 días")
        return
    
    # Sort by due date
    upcoming.sort(key=lambda x: x['due_date'])
    
    st.subheader("📅 Próximos Pagos (30 días)")
    
    for payment in upcoming:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{payment['name']}**")
        
        with col2:
            st.write(f"{payment['currency']} {payment['amount']:,.2f}")
        
        with col3:
            if payment['days_left'] == 0:
                st.error("¡Hoy!")
            elif payment['days_left'] <= 3:
                st.warning(f"{payment['days_left']} días")
            else:
                st.info(f"{payment['days_left']} días")