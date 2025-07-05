#!/bin/bash

# 🚀 Script de inicio rápido para Finanzas Personales
# Este script inicia tanto el backend como el frontend automáticamente

set -e  # Exit on any error

echo "🚀 Iniciando Sistema de Finanzas Personales..."
echo "⏰ $(date)"
echo ""

# Verificar que estamos en el directorio correcto
if [[ ! -f "requirements.txt" ]]; then
    echo "❌ Error: No se encontró requirements.txt"
    echo "   Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar que existe el entorno virtual
if [[ ! -d "venv" ]]; then
    echo "❌ Error: No se encontró el entorno virtual 'venv'"
    echo "   Ejecuta: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Verificar variables de entorno
if [[ ! -f ".env" ]]; then
    echo "⚠️  Advertencia: No se encontró archivo .env"
    echo "   Copiando .env.example -> .env"
    cp .env.example .env
    echo "   Por favor, edita .env con tus configuraciones antes de continuar"
fi

# Verificar PostgreSQL
echo "🔍 Verificando conexión a PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "⚠️  psql no está disponible. Asegúrate de que PostgreSQL esté instalado"
else
    # Intentar conectar (usando variables del .env si existen)
    source .env 2>/dev/null || true
    DB_HOST=${DB_HOST:-localhost}
    DB_USER=${DB_USER:-finanzas_user}
    DB_NAME=${DB_NAME:-finanzas_db}
    
    if PGPASSWORD=${DB_PASSWORD:-finanzas_pass} psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" &>/dev/null; then
        echo "✅ Conexión a PostgreSQL exitosa"
    else
        echo "⚠️  No se pudo conectar a PostgreSQL. Verifica la configuración en .env"
        echo "   Host: $DB_HOST, Usuario: $DB_USER, Base de datos: $DB_NAME"
    fi
fi

echo ""
echo "🚀 Iniciando servicios..."

# Crear archivo para almacenar PIDs
PID_FILE="/tmp/finanzas_personales.pids"
echo "" > "$PID_FILE"

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    
    if [[ -f "$PID_FILE" ]]; then
        while read -r pid; do
            if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
                echo "   Deteniendo proceso $pid"
                kill "$pid" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
    
    echo "✅ Servicios detenidos"
    exit 0
}

# Configurar trap para limpiar al salir
trap cleanup SIGINT SIGTERM

# Iniciar Backend
echo "🔧 Iniciando Backend (FastAPI)..."
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "$BACKEND_PID" >> "$PID_FILE"
cd ..

# Esperar un momento para que el backend inicie
sleep 3

# Verificar que el backend esté corriendo
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "⚠️  Backend no responde en http://localhost:8000"
else
    echo "✅ Backend iniciado correctamente"
fi

# Iniciar Frontend
echo "🎨 Iniciando Frontend (Streamlit)..."
cd frontend
source ../venv/bin/activate
streamlit run main.py --server.port 8501 --server.headless true &
FRONTEND_PID=$!
echo "$FRONTEND_PID" >> "$PID_FILE"
cd ..

# Esperar un momento para que el frontend inicie
sleep 5

echo ""
echo "🎉 ¡Sistema iniciado correctamente!"
echo ""
echo "📱 Accesos:"
echo "   🌐 Frontend: http://localhost:8501"
echo "   🔧 Backend API: http://localhost:8000"
echo "   📚 Documentación API: http://localhost:8000/docs"
echo "   📖 ReDoc: http://localhost:8000/redoc"
echo ""
echo "💡 Para detener los servicios: Presiona Ctrl+C"
echo ""
echo "📊 Estado de servicios:"

# Verificar estado de servicios
check_service() {
    local url=$1
    local name=$2
    
    if curl -s "$url" > /dev/null; then
        echo "   ✅ $name: Funcionando"
    else
        echo "   ❌ $name: No responde"
    fi
}

check_service "http://localhost:8000/health" "Backend"
check_service "http://localhost:8501" "Frontend"

echo ""
echo "🔍 Logs en tiempo real:"
echo "   Backend: tail -f logs/finanzas.log"
echo "   Frontend: tail -f frontend/streamlit.log"
echo ""
echo "⏳ Servicios corriendo... (Ctrl+C para detener)"

# Esperar indefinidamente hasta que el usuario presione Ctrl+C
wait