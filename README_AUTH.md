# Implementación de Autenticación con Supabase en el Backend

Este documento describe la implementación de la autenticación con Supabase en el backend de la aplicación de insectos.

## Descripción General

Hemos movido la lógica de autenticación de Supabase del frontend (Flutter) al backend (FastAPI) para mejorar la seguridad de la aplicación. Esto proporciona varias ventajas:

1. Las credenciales de Supabase no están expuestas en el código del cliente
2. El backend actúa como un intermediario para todas las operaciones de autenticación
3. Se pueden implementar políticas de seguridad adicionales en el backend
4. Mayor control sobre los tokens de autenticación y su validación

## Estructura de la Implementación

La implementación consta de los siguientes componentes:

### 1. Servicio de Supabase (`services/supabase_service.py`)

Este servicio maneja todas las interacciones con la API de Supabase, incluyendo:
- Inicio de sesión con email y contraseña
- Registro de nuevos usuarios
- Restablecimiento de contraseñas
- Autenticación con proveedores OAuth (Google, etc.)
- Actualización de metadatos de usuario
- Verificación de tokens

### 2. Router de Autenticación (`routers/auth.py`)

Expone endpoints REST para las operaciones de autenticación:
- `/api/auth/login`: Iniciar sesión con email y contraseña
- `/api/auth/signup`: Registrar un nuevo usuario
- `/api/auth/reset-password`: Solicitar restablecimiento de contraseña
- `/api/auth/refresh-token`: Refrescar un token expirado
- `/api/auth/signout`: Cerrar sesión
- `/api/auth/update-metadata`: Actualizar metadatos del usuario
- `/api/auth/user`: Obtener información del usuario actual
- `/api/auth/oauth`: Iniciar flujo de autenticación OAuth
- `/api/auth/exchange-code`: Intercambiar código de autenticación por sesión

### 3. Middleware de Autenticación (`middleware/auth_middleware.py`)

Proporciona funciones para verificar y validar tokens JWT:
- `get_current_user`: Dependencia para rutas que requieren autenticación
- `get_optional_user`: Dependencia para rutas que pueden funcionar con o sin autenticación

### 4. Rutas Protegidas

Hemos implementado ejemplos de rutas protegidas que requieren autenticación:
- `/api/insects/favorites/list`: Obtener la lista de insectos favoritos del usuario
- `/api/insects/favorites/add/{insect_id}`: Agregar un insecto a la lista de favoritos

## Configuración

Para configurar la autenticación de Supabase en el backend:

1. Ejecuta el script `setup_auth.py` para instalar las dependencias necesarias y configurar el archivo `.env`

```bash
python setup_auth.py
```

2. Edita el archivo `.env` y configura las siguientes variables:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

> **IMPORTANTE**: Usa la clave `service_role` de Supabase, NO la clave `anon`. La clave `service_role` tiene permisos elevados y solo debe usarse en el backend.

## Uso en el Frontend

El frontend ahora debe comunicarse con el backend para todas las operaciones de autenticación. Hemos actualizado el controlador de autenticación en el frontend para usar el nuevo servicio de autenticación.

### Ejemplo de inicio de sesión:

```dart
// Antes (directamente con Supabase)
await _supabase.auth.signInWithPassword(
  email: email,
  password: password,
);

// Ahora (a través del backend)
final result = await _authService.signInWithEmail(email, password);
if (result['success']) {
  // Procesar los datos de la sesión
  final sessionData = result['session'];
  final userData = result['user'];
  // ...
}
```

## Protección de Rutas

Para proteger una ruta en el backend y requerir autenticación, usa la dependencia `get_current_user`:

```python
@router.get("/protected-route")
async def protected_endpoint(
    user_data: Dict[str, Any] = Depends(get_current_user)
):
    # El usuario está autenticado, puedes acceder a sus datos
    user_id = user_data.get("id")
    # ...
    return {"message": "Ruta protegida accedida correctamente"}
```

## Pruebas

Para probar la autenticación, puedes usar herramientas como Postman o curl:

```bash
# Iniciar sesión
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@ejemplo.com", "password": "contraseña"}'

# Acceder a una ruta protegida con el token obtenido
curl -X GET http://localhost:8000/api/insects/favorites/list \
  -H "Authorization: Bearer tu-token-jwt"
```

## Consideraciones de Seguridad

1. **Variables de Entorno**: Nunca cometas el archivo `.env` en el repositorio. Asegúrate de que esté en `.gitignore`.

2. **HTTPS**: En producción, asegúrate de que todas las comunicaciones entre el frontend y el backend se realicen a través de HTTPS.

3. **Validación de Tokens**: El backend valida los tokens JWT antes de permitir el acceso a rutas protegidas.

4. **Expiración de Tokens**: Implementa la renovación automática de tokens cuando estén próximos a expirar.

5. **Almacenamiento Seguro**: En el frontend, almacena los tokens de forma segura (por ejemplo, usando `flutter_secure_storage` en dispositivos móviles).

## Próximos Pasos

1. Implementar almacenamiento seguro de tokens en el frontend
2. Añadir funcionalidad para gestionar roles y permisos de usuario
3. Implementar límites de tasa (rate limiting) para prevenir ataques de fuerza bruta
4. Añadir autenticación de dos factores (2FA)
