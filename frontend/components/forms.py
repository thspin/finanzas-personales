import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from .api_client import get_api_client
from .ui_helpers import (
    show_loading_spinner, show_success_message, show_error_message, show_warning_message,
    validate_amount_real_time, validate_required_fields, enhanced_number_input,
    enhanced_text_input, enhanced_selectbox, handle_api_error, with_error_handling,
    check_duplicate_transaction
)


def product_selector(
    products: List[Dict[str, Any]], 
    key: str = "product_selector",
    label: str = "Seleccionar Producto",
    currency_filter: Optional[str] = None
) -> Optional[int]:
    """
    Render enhanced product selector grouped by institution
    """
    if not products:
        show_warning_message("No hay productos disponibles")
        return None
    
    # Filter by currency if specified
    if currency_filter:
        products = [p for p in products if p['currency']['code'] == currency_filter]
        if not products:
            show_warning_message(f"No hay productos en {currency_filter}")
            return None
    
    # Group products by institution
    institutions = {}
    for product in products:
        inst_name = product['institution']['name']
        if inst_name not in institutions:
            institutions[inst_name] = []
        institutions[inst_name].append(product)
    
    # Create options list
    options = []
    product_map = {}
    
    for inst_name, inst_products in institutions.items():
        for product in inst_products:
            display_name = f"{inst_name} - {product['product_type']}"
            if product.get('identifier'):
                display_name += f" ({product['identifier']})"
            display_name += f" [{product['currency']['symbol']}]"
            
            options.append(display_name)
            product_map[display_name] = product['id']
    
    selected = enhanced_selectbox(
        label, 
        options, 
        key=key,
        help_text="Selecciona el producto donde se registrará la operación",
        empty_label="Selecciona un producto..."
    )
    
    if selected is None:
        return None
    
    return product_map[selected]


def currency_selector_buttons(
    currencies: List[Dict[str, Any]], 
    key: str = "currency_selector",
    label: str = "Moneda"
) -> Optional[str]:
    """
    Render currency selector with interactive buttons
    """
    if not currencies:
        show_warning_message("No hay monedas disponibles")
        return None
    
    st.markdown(f"**{label}**")
    st.caption("Selecciona la moneda para esta operación")
    
    # Create columns for currency buttons
    max_cols = min(len(currencies), 4)  # Max 4 columns
    cols = st.columns(max_cols)
    
    selected_currency = None
    
    for i, currency in enumerate(currencies):
        col_index = i % max_cols
        with cols[col_index]:
            # Create button with currency info
            button_label = f"{currency['symbol']} {currency['code']}"
            button_help = f"{currency['name']}"
            
            if st.button(
                button_label,
                key=f"{key}_{currency['code']}",
                help=button_help,
                use_container_width=True
            ):
                selected_currency = currency['code']
                # Store selection in session state for persistence
                st.session_state[f"{key}_selected"] = selected_currency
    
    # Return stored selection or current selection
    return selected_currency or st.session_state.get(f"{key}_selected")


def currency_selector(
    currencies: List[Dict[str, Any]], 
    key: str = "currency_selector",
    label: str = "Moneda"
) -> Optional[str]:
    """
    Render enhanced currency selector (fallback method)
    """
    if not currencies:
        show_warning_message("No hay monedas disponibles")
        return None
    
    options = [
        f"{curr['code']} - {curr['name']} ({curr['symbol']})" 
        for curr in currencies
    ]
    
    selected = enhanced_selectbox(
        label, 
        options, 
        key=key,
        help_text="Selecciona la moneda para esta operación",
        empty_label="Selecciona una moneda..."
    )
    
    if selected is None:
        return None
    
    # Extract currency code
    return selected.split(" - ")[0]


def category_selector(
    categories: List[Dict[str, Any]], 
    category_type: str,
    key: str = "category_selector",
    label: str = "Categoría"
) -> Optional[str]:
    """
    Render enhanced category selector filtered by type
    """
    filtered_categories = [
        cat for cat in categories 
        if cat['type'] == category_type
    ]
    
    if not filtered_categories:
        show_warning_message(f"No hay categorías de tipo {category_type}")
        return None
    
    options = [
        f"{cat['emoji']} {cat['name']}" 
        for cat in filtered_categories
    ]
    
    type_text = "ingresos" if category_type == "INCOME" else "egresos"
    selected = enhanced_selectbox(
        label, 
        options, 
        key=key,
        help_text=f"Selecciona la categoría para {type_text}",
        empty_label="Selecciona una categoría..."
    )
    
    if selected is None:
        return None
    
    # Extract category name (remove emoji)
    return selected.split(" ", 1)[1]


def institution_selector_or_create(
    institutions: List[Dict[str, Any]],
    key: str = "institution_selector"
) -> Dict[str, Any]:
    """
    Render enhanced institution selector with option to create new one
    Returns dict with 'type': 'existing'/'new' and relevant data
    """
    option = st.radio(
        "Institución",
        ["Seleccionar existente", "Crear nueva"],
        key=f"{key}_option",
        help="Elige una institución existente o crea una nueva"
    )
    
    if option == "Seleccionar existente":
        if not institutions:
            show_warning_message("No hay instituciones disponibles. Crea una nueva.")
            return {"type": "none"}
        
        options = [inst['name'] for inst in institutions]
        selected = enhanced_selectbox(
            "Institución", 
            options, 
            key=f"{key}_select",
            help_text="Selecciona la institución financiera",
            empty_label="Selecciona una institución..."
        )
        
        if selected is None:
            return {"type": "none"}
        
        selected_institution = next(
            inst for inst in institutions if inst['name'] == selected
        )
        return {"type": "existing", "data": selected_institution}
    
    else:  # Create new
        name, name_validation = enhanced_text_input(
            "Nombre de la institución", 
            placeholder="Ej: Banco Galicia",
            key=f"{key}_name",
            help_text="Ingresa el nombre completo de la institución"
        )
        
        logo_url, _ = enhanced_text_input(
            "URL del logo (opcional)", 
            placeholder="https://ejemplo.com/logo.png",
            key=f"{key}_logo",
            help_text="URL de la imagen del logo (opcional)"
        )
        
        if name and name_validation["valid"]:
            return {
                "type": "new", 
                "data": {
                    "name": name,
                    "logo_url": logo_url if logo_url else None
                }
            }
        
        return {"type": "none"}


def transaction_form(
    products: List[Dict[str, Any]], 
    currencies: List[Dict[str, Any]], 
    categories: List[Dict[str, Any]]
):
    """
    Render enhanced transaction creation form with improved flow
    """
    api = get_api_client()
    
    st.subheader("💰 Nueva Transacción")
    
    # Step 1: Transaction type (outside form for better UX)
    transaction_type = st.radio(
        "Tipo de Transacción",
        ["INCOME", "EXPENSE"],
        format_func=lambda x: "💰 Ingreso" if x == "INCOME" else "💸 Egreso",
        help="Selecciona si es dinero que entra o sale de tu cuenta",
        key="trans_type_select"
    )
    
    # Step 2: Currency selection (outside form for reactivity)
    st.markdown("#### 1️⃣ Seleccionar Moneda")
    currency_code = currency_selector_buttons(currencies, "trans_currency", "Moneda")
    
    if not currency_code:
        st.info("👆 Selecciona una moneda para continuar")
        return
    
    # Step 3: Product selection (filtered by currency)
    st.markdown("#### 2️⃣ Seleccionar Producto")
    product_id = product_selector(
        products, 
        "trans_product", 
        "Producto", 
        currency_filter=currency_code
    )
    
    if not product_id:
        st.info("👆 Selecciona un producto para continuar")
        return
    
    # Step 4: Now show the form with remaining fields
    st.markdown("#### 3️⃣ Completar Transacción")
    
    with st.form("transaction_form"):
        # Category selection (filtered by transaction type)
        category = category_selector(
            categories, 
            transaction_type, 
            "trans_category", 
            "Categoría"
        )
        
        # Enhanced amount input with real-time validation
        amount, amount_validation = enhanced_number_input(
            "Monto", 
            min_value=0.01,
            max_value=999999999.99,
            key="trans_amount",
            help_text="Ingresa el monto de la transacción",
            currency_symbol=next((c['symbol'] for c in currencies if c['code'] == currency_code), "$")
        )
        
        # Enhanced description input
        description, desc_validation = enhanced_text_input(
            "Descripción (opcional)", 
            placeholder="Ej: Compra en supermercado",
            max_chars=200,
            key="trans_desc",
            help_text="Descripción detallada de la transacción"
        )
        
        transaction_date = st.date_input(
            "Fecha", 
            value=date.today(),
            key="trans_date",
            help="Fecha en que ocurrió la transacción"
        )
        
        # Real-time validation summary
        validation_fields = {
            "Producto": product_id,
            "Categoría": category,
            "Monto": amount if amount_validation["valid"] else None
        }
        
        field_validation = validate_required_fields(validation_fields)
        
        # Check for potential duplicates if we have enough data
        duplicate_check = {"duplicate": False}
        if product_id and description and amount and amount_validation["valid"]:
            try:
                # Get recent transactions for duplicate checking
                recent_transactions = api.get_transactions_by_product(product_id)
                duplicate_check = check_duplicate_transaction(
                    description, amount, transaction_date, recent_transactions
                )
                if duplicate_check["duplicate"]:
                    show_warning_message(duplicate_check["message"])
            except:
                pass  # Don't fail form if duplicate check fails
        
        # Submit button with validation-based state
        can_submit = (
            field_validation["valid"] and 
            amount_validation["valid"] and
            not duplicate_check["duplicate"]
        )
        
        submitted = st.form_submit_button(
            "Crear Transacción", 
            type="primary",
            disabled=not can_submit
        )
        
        if submitted:
            if not can_submit:
                show_error_message("Por favor corrige los errores antes de continuar")
                return
            
            def create_transaction():
                transaction_data = {
                    "product_id": product_id,
                    "type": transaction_type,
                    "transaction_date": transaction_date.isoformat(),
                    "category": category,
                    "description": description,
                    "amount": float(amount)
                }
                
                with show_loading_spinner("Creando transacción..."):
                    return api.create_transaction(transaction_data)
            
            result = with_error_handling(create_transaction, "crear transacción")
            
            if result:
                show_success_message("¡Transacción creada exitosamente!")
                st.rerun()
        
        # Enhanced description input
        description, desc_validation = enhanced_text_input(
            "Descripción (opcional)", 
            placeholder="Ej: Compra en supermercado",
            max_chars=200,
            key="trans_desc",
            help_text="Descripción detallada de la transacción"
        )
        
        transaction_date = st.date_input(
            "Fecha", 
            value=date.today(),
            key="trans_date",
            help="Fecha en que ocurrió la transacción"
        )
        
        # Real-time validation summary
        validation_fields = {
            "Producto": product_id,
            "Categoría": category,
            "Monto": amount if amount_validation["valid"] else None
        }
        
        field_validation = validate_required_fields(validation_fields)
        
        # Check for potential duplicates if we have enough data
        duplicate_check = {"duplicate": False}
        if product_id and description and amount and amount_validation["valid"]:
            try:
                # Get recent transactions for duplicate checking
                recent_transactions = api.get_transactions_by_product(product_id)
                duplicate_check = check_duplicate_transaction(
                    description, amount, transaction_date, recent_transactions
                )
                if duplicate_check["duplicate"]:
                    show_warning_message(duplicate_check["message"])
            except:
                pass  # Don't fail form if duplicate check fails
        
        # Submit button with validation-based state
        can_submit = (
            field_validation["valid"] and 
            amount_validation["valid"] and
            not duplicate_check["duplicate"]
        )
        
        submitted = st.form_submit_button(
            "Crear Transacción", 
            type="primary",
            disabled=not can_submit
        )
        
        if submitted:
            if not can_submit:
                show_error_message("Por favor corrige los errores antes de continuar")
                return
            
            def create_transaction():
                transaction_data = {
                    "product_id": product_id,
                    "type": transaction_type,
                    "transaction_date": transaction_date.isoformat(),
                    "category": category,
                    "description": description,
                    "amount": float(amount)
                }
                
                with show_loading_spinner("Creando transacción..."):
                    return api.create_transaction(transaction_data)
            
            result = with_error_handling(create_transaction, "crear transacción")
            
            if result:
                show_success_message("¡Transacción creada exitosamente!")
                st.rerun()


def credit_form(
    products: List[Dict[str, Any]]
):
    """
    Render enhanced credit creation form with real-time validation
    """
    api = get_api_client()
    
    with st.form("credit_form"):
        st.subheader("🏧 Nuevo Crédito")
        
        # Filter products to only credit cards
        credit_products = [
            p for p in products 
            if p['product_type'].upper() in ['CREDIT_CARD', 'TARJETA DE CRÉDITO', 'CREDITO']
        ]
        
        if not credit_products:
            show_warning_message("No hay productos de tipo 'Tarjeta de Crédito' disponibles")
            st.form_submit_button("Crear Crédito", disabled=True)
            return
        
        product_id = product_selector(
            credit_products, 
            "credit_product", 
            "Tarjeta de Crédito"
        )
        
        if not product_id:
            show_warning_message("Selecciona una tarjeta de crédito")
            st.form_submit_button("Crear Crédito", disabled=True)
            return
        
        # Enhanced description input
        description, desc_validation = enhanced_text_input(
            "Descripción de la compra", 
            placeholder="Ej: Notebook Lenovo",
            max_chars=200,
            key="credit_desc",
            help_text="Describe qué compraste en cuotas"
        )
        
        # Get currency from selected product
        selected_product = next((p for p in credit_products if p['id'] == product_id), None)
        currency_symbol = selected_product['currency']['symbol'] if selected_product else "$"
        
        # Enhanced amount input
        total_amount, amount_validation = enhanced_number_input(
            "Monto Total", 
            min_value=0.01,
            max_value=9999999.99,
            key="credit_amount",
            help_text="Monto total de la compra en cuotas",
            currency_symbol=currency_symbol
        )
        
        total_installments = st.number_input(
            "Número de Cuotas", 
            min_value=1, 
            max_value=60, 
            value=12,
            key="credit_installments",
            help="Cantidad de cuotas en las que se dividirá el pago"
        )
        
        # Show installment preview
        if total_amount > 0 and total_installments > 0:
            installment_amount = total_amount / total_installments
            st.info(f"💡 Cada cuota será de aproximadamente {currency_symbol} {installment_amount:,.2f}")
        
        purchase_date = st.date_input(
            "Fecha de Compra", 
            value=date.today(),
            key="credit_date",
            help="Fecha en que realizaste la compra"
        )
        
        # Option for custom installment amounts
        custom_amounts = st.checkbox(
            "Montos personalizados por cuota",
            help="Marca si las cuotas tienen montos diferentes"
        )
        
        installment_amounts = None
        installments_valid = True
        
        if custom_amounts and total_installments > 0:
            st.write("**Montos por cuota:**")
            amounts = []
            total_custom = 0
            
            for i in range(int(total_installments)):
                amount, _ = enhanced_number_input(
                    f"Cuota {i+1}", 
                    min_value=0.01,
                    value=float(total_amount / total_installments) if total_amount > 0 else 0.01,
                    key=f"installment_{i}",
                    currency_symbol=currency_symbol
                )
                amounts.append(amount)
                total_custom += amount
            
            installment_amounts = amounts
            
            # Validate that custom amounts match total
            if abs(total_custom - total_amount) > 0.01:
                difference = total_custom - total_amount
                if difference > 0:
                    show_warning_message(f"Las cuotas suman {currency_symbol} {difference:,.2f} más que el total")
                else:
                    show_warning_message(f"Las cuotas suman {currency_symbol} {abs(difference):,.2f} menos que el total")
                installments_valid = False
        
        # Real-time validation summary
        validation_fields = {
            "Producto": product_id,
            "Descripción": description if desc_validation["valid"] else None,
            "Monto": total_amount if amount_validation["valid"] else None,
            "Cuotas": total_installments
        }
        
        field_validation = validate_required_fields(validation_fields)
        
        can_submit = (
            field_validation["valid"] and 
            amount_validation["valid"] and 
            desc_validation["valid"] and
            installments_valid
        )
        
        submitted = st.form_submit_button(
            "Crear Crédito", 
            type="primary",
            disabled=not can_submit
        )
        
        if submitted:
            if not can_submit:
                show_error_message("Por favor corrige los errores antes de continuar")
                return
            
            def create_credit():
                credit_data = {
                    "product_id": product_id,
                    "description": description,
                    "total_amount": float(total_amount),
                    "total_installments": int(total_installments),
                    "purchase_date": purchase_date.isoformat(),
                    "installment_amounts": installment_amounts
                }
                
                with show_loading_spinner("Creando crédito..."):
                    return api.create_credit(credit_data)
            
            result = with_error_handling(create_credit, "crear crédito")
            
            if result:
                show_success_message("¡Crédito creado exitosamente!")
                st.rerun()


def service_form(
    products: List[Dict[str, Any]], 
    currencies: List[Dict[str, Any]]
):
    """
    Render enhanced service creation form with real-time validation
    """
    api = get_api_client()
    
    with st.form("service_form"):
        st.subheader("📋 Nuevo Servicio/Suscripción")
        
        # Enhanced name input
        name, name_validation = enhanced_text_input(
            "Nombre del servicio", 
            placeholder="Ej: Netflix, Spotify, Internet",
            max_chars=100,
            key="service_name",
            help_text="Nombre del servicio o suscripción"
        )
        
        description, _ = enhanced_text_input(
            "Descripción (opcional)", 
            placeholder="Detalles adicionales del servicio",
            max_chars=200,
            key="service_desc",
            help_text="Descripción opcional del servicio"
        )
        
        # Currency selection first
        currency_code = currency_selector(currencies, "service_currency", "Moneda")
        
        if not currency_code:
            show_warning_message("Selecciona una moneda primero")
            st.form_submit_button("Crear Servicio", disabled=True)
            return
        
        # Get currency symbol
        currency_symbol = next((c['symbol'] for c in currencies if c['code'] == currency_code), "$")
        
        # Enhanced amount input
        amount, amount_validation = enhanced_number_input(
            "Monto", 
            min_value=0.01,
            max_value=999999.99,
            key="service_amount",
            help_text="Monto que se paga por período",
            currency_symbol=currency_symbol
        )
        
        frequency = enhanced_selectbox(
            "Frecuencia",
            ["MONTHLY", "ANNUAL", "WEEKLY", "QUARTERLY"],
            format_func=lambda x: {
                "MONTHLY": "📅 Mensual",
                "ANNUAL": "📆 Anual", 
                "WEEKLY": "🗓️ Semanal",
                "QUARTERLY": "📊 Trimestral"
            }[x] if x else "Seleccionar...",
            key="service_frequency",
            help_text="Con qué frecuencia se cobra este servicio",
            empty_label="Selecciona frecuencia..."
        )
        
        if not frequency:
            show_warning_message("Selecciona la frecuencia de pago")
            st.form_submit_button("Crear Servicio", disabled=True)
            return
        
        payment_day = st.number_input(
            "Día de pago (1-31)", 
            min_value=1, 
            max_value=31, 
            value=1,
            key="service_payment_day",
            help="Día del mes en que se cobra (para servicios mensuales)"
        )
        
        payment_type = st.radio(
            "Tipo de pago",
            ["AUTO", "MANUAL"],
            format_func=lambda x: "🔄 Automático (débito desde producto)" if x == "AUTO" else "📝 Manual (recordatorio)",
            key="service_payment_type",
            help="Cómo se maneja el pago de este servicio"
        )
        
        product_id = None
        if payment_type == "AUTO":
            if currency_code:
                product_id = product_selector(
                    products, 
                    "service_product", 
                    "Producto para débito", 
                    currency_filter=currency_code
                )
                
                if not product_id:
                    show_warning_message("Selecciona un producto para el débito automático")
        
        next_due_date = st.date_input(
            "Próximo vencimiento", 
            value=date.today() + timedelta(days=30),
            key="service_due_date",
            help="Fecha del próximo pago de este servicio"
        )
        
        # Show payment preview
        if amount > 0 and frequency:
            freq_text = {
                "MONTHLY": "mensual",
                "ANNUAL": "anual",
                "WEEKLY": "semanal",
                "QUARTERLY": "trimestral"
            }.get(frequency, "")
            
            if freq_text:
                st.info(f"💡 Pago {freq_text} de {currency_symbol} {amount:,.2f}")
        
        # Real-time validation summary
        validation_fields = {
            "Nombre": name if name_validation["valid"] else None,
            "Monto": amount if amount_validation["valid"] else None,
            "Moneda": currency_code,
            "Frecuencia": frequency
        }
        
        if payment_type == "AUTO":
            validation_fields["Producto para débito"] = product_id
        
        field_validation = validate_required_fields(validation_fields)
        
        can_submit = (
            field_validation["valid"] and 
            name_validation["valid"] and 
            amount_validation["valid"]
        )
        
        submitted = st.form_submit_button(
            "Crear Servicio", 
            type="primary",
            disabled=not can_submit
        )
        
        if submitted:
            if not can_submit:
                show_error_message("Por favor corrige los errores antes de continuar")
                return
            
            def create_service():
                # Get currency ID
                currency = next(c for c in currencies if c['code'] == currency_code)
                
                service_data = {
                    "name": name,
                    "description": description,
                    "amount": float(amount),
                    "currency_id": currency['id'],
                    "frequency": frequency,
                    "payment_day": int(payment_day),
                    "payment_type": payment_type,
                    "next_due_date": next_due_date.isoformat(),
                    "product_id": product_id
                }
                
                with show_loading_spinner("Creando servicio..."):
                    return api.create_service(service_data)
            
            result = with_error_handling(create_service, "crear servicio")
            
            if result:
                show_success_message("¡Servicio creado exitosamente!")
                st.rerun()


def notification_bell():
    """
    Render notification bell with count
    """
    api = get_api_client()
    
    try:
        # Get notification count
        count_data = api.get_notification_count()
        unread_count = count_data.get('unread_count', 0)
        
        # Display bell with count
        if unread_count > 0:
            if st.button(f"🔔 {unread_count}", key="notification_bell"):
                st.session_state.show_notifications = True
                st.rerun()
        else:
            if st.button("🔕", key="notification_bell_empty"):
                st.session_state.show_notifications = True
                st.rerun()
    
    except Exception as e:
        st.error(f"Error al cargar notificaciones: {str(e)}")


def render_notifications_sidebar():
    """
    Render notifications in sidebar
    """
    if not st.session_state.get('show_notifications', False):
        return
    
    api = get_api_client()
    
    with st.sidebar:
        st.markdown("### 🔔 Notificaciones")
        
        try:
            notifications = api.get_notifications()
            
            if not notifications:
                st.info("No hay notificaciones")
            else:
                for notif in notifications[:5]:  # Show last 5
                    with st.container():
                        st.markdown(f"**{notif['title']}**")
                        st.markdown(notif['message'])
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if not notif['is_read']:
                                if st.button("✓", key=f"read_{notif['id']}"):
                                    api.mark_notification_read(notif['id'])
                                    st.rerun()
                        
                        with col2:
                            if st.button("🗑️", key=f"delete_{notif['id']}"):
                                api.delete_notification(notif['id'])
                                st.rerun()
                        
                        st.markdown("---")
            
            # Mark all as read button
            if st.button("Marcar todas como leídas"):
                api.mark_all_notifications_read()
                st.rerun()
            
            # Close notifications
            if st.button("Cerrar"):
                st.session_state.show_notifications = False
                st.rerun()
        
        except Exception as e:
            st.error(f"Error al cargar notificaciones: {str(e)}")