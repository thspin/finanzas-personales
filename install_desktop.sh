#!/bin/bash

# Script para instalar el acceso directo de Finanzas Personales

echo "🚀 Instalando acceso directo de Finanzas Personales..."

# Directorio de aplicaciones del usuario
DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="finanzas-personales.desktop"
SOURCE_FILE="/home/thspin/finanzas-personales/$DESKTOP_FILE"

# Crear directorio si no existe
mkdir -p "$DESKTOP_DIR"

# Copiar archivo .desktop
if [ -f "$SOURCE_FILE" ]; then
    cp "$SOURCE_FILE" "$DESKTOP_DIR/"
    chmod +x "$DESKTOP_DIR/$DESKTOP_FILE"
    echo "✅ Acceso directo instalado en: $DESKTOP_DIR/$DESKTOP_FILE"
else
    echo "❌ Error: No se encontró el archivo $SOURCE_FILE"
    exit 1
fi

# Actualizar base de datos de aplicaciones
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR"
    echo "✅ Base de datos de aplicaciones actualizada"
fi

# Copiar también al escritorio si existe
DESKTOP_PATH="$HOME/Desktop"
if [ -d "$DESKTOP_PATH" ]; then
    cp "$SOURCE_FILE" "$DESKTOP_PATH/"
    chmod +x "$DESKTOP_PATH/$DESKTOP_FILE"
    echo "✅ Acceso directo copiado al escritorio: $DESKTOP_PATH/$DESKTOP_FILE"
fi

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "📋 Ahora puedes:"
echo "   • Buscar 'Finanzas Personales' en el menú de aplicaciones"
echo "   • Hacer doble clic en el icono del escritorio"
echo "   • Acceder desde el lanzador de aplicaciones"
echo ""
echo "🔗 URLs del sistema:"
echo "   • Frontend: http://localhost:8501"
echo "   • API Backend: http://localhost:8000"
echo "   • Documentación API: http://localhost:8000/docs"
echo ""
echo "⚡ El sistema se iniciará automáticamente con todos los servicios."