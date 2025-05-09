import time
from typing import Dict, Any, Optional, Tuple

class CacheService:
    """
    Servicio de caché en memoria simple con tiempo de expiración.
    """
    def __init__(self, ttl_seconds: int = 86400):  # 24 horas por defecto
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor de la caché si existe y no ha expirado.
        
        Args:
            key: Clave para buscar en la caché
            
        Returns:
            El valor almacenado o None si no existe o ha expirado
        """
        if key not in self.cache:
            return None
            
        value, timestamp = self.cache[key]
        current_time = time.time()
        
        # Verificar si el valor ha expirado
        if current_time - timestamp > self.ttl_seconds:
            # Eliminar el valor expirado
            del self.cache[key]
            return None
            
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Almacena un valor en la caché con la marca de tiempo actual.
        
        Args:
            key: Clave para almacenar el valor
            value: Valor a almacenar
        """
        self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """
        Limpia toda la caché.
        """
        self.cache.clear()
    
    def remove(self, key: str) -> None:
        """
        Elimina una clave específica de la caché.
        
        Args:
            key: Clave a eliminar
        """
        if key in self.cache:
            del self.cache[key]
    
    def get_size(self) -> int:
        """
        Retorna el número de elementos en la caché.
        
        Returns:
            Número de elementos en la caché
        """
        return len(self.cache)
