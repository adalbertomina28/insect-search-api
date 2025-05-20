#!/usr/bin/env python3
"""
Script para configurar la autenticación de Supabase en el backend.
Este script instala las dependencias necesarias y configura el archivo .env.
"""

import os
import sys
import subprocess
import re

def check_supabase_env():
    """Verifica si las variables de entorno de Supabase están configuradas en el archivo .env"""
    env_file = '.env'
    
    # Verificar si el archivo .env existe
    if not os.path.exists(env_file):
        print("El archivo .env no existe. Creando uno nuevo...")
        with open(env_file, 'w') as f:
            f.write("# Configuración de Supabase\n")
            f.write("SUPABASE_URL=\n")
            f.write("SUPABASE_SERVICE_KEY=\n\n")
            f.write("# Configuración de la API de iNaturalist\n")
            f.write("INATURALIST_API_TOKEN=\n")
            f.write("INATURALIST_JWT_TOKEN=\n\n")
            f.write("# Configuración de logging\n")
            f.write("LOG_LEVEL=INFO\n")
        print("Archivo .env creado. Por favor, configura las variables de entorno de Supabase.")
        return False
    
    # Leer el archivo .env
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    # Verificar si las variables de entorno de Supabase están configuradas
    supabase_url = re.search(r'SUPABASE_URL=(.+)', env_content)
    supabase_key = re.search(r'SUPABASE_SERVICE_KEY=(.+)', env_content)
    
    if not supabase_url or not supabase_key or not supabase_url.group(1) or not supabase_key.group(1):
        print("Las variables de entorno de Supabase no están configuradas en el archivo .env.")
        print("Por favor, configura SUPABASE_URL y SUPABASE_SERVICE_KEY en el archivo .env.")
        return False
    
    print("Variables de entorno de Supabase configuradas correctamente.")
    return True

def install_dependencies():
    """Instala las dependencias necesarias para la autenticación de Supabase"""
    print("Instalando dependencias...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencias instaladas correctamente.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar dependencias: {e}")
        return False

def main():
    """Función principal"""
    print("=== Configuración de Autenticación de Supabase ===")
    
    # Instalar dependencias
    if not install_dependencies():
        print("No se pudieron instalar las dependencias. Abortando.")
        return
    
    # Verificar variables de entorno
    if not check_supabase_env():
        print("\nPara completar la configuración, sigue estos pasos:")
        print("1. Abre el archivo .env")
        print("2. Configura SUPABASE_URL con la URL de tu proyecto de Supabase (ej: https://your-project-id.supabase.co)")
        print("3. Configura SUPABASE_SERVICE_KEY con la clave de servicio de tu proyecto de Supabase")
        print("   (Esta es la 'service_role key', NO la 'anon key')")
        print("\nPuedes encontrar estas credenciales en el panel de control de Supabase:")
        print("- Ve a https://app.supabase.io")
        print("- Selecciona tu proyecto")
        print("- Ve a 'Settings' > 'API'")
        print("- Copia la URL y la 'service_role key'")
        return
    
    print("\n=== Configuración completada ===")
    print("La autenticación de Supabase está configurada correctamente.")
    print("Puedes iniciar el servidor con 'python main.py'")

if __name__ == "__main__":
    main()
