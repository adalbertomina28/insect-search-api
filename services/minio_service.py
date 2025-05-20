import os
import uuid
import logging
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
import tempfile
import shutil
import mimetypes
from urllib.parse import urljoin

# Intentar importar python-magic, pero proporcionar una alternativa si falla
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    logging.warning("python-magic no está disponible, usando mimetypes como alternativa")


logger = logging.getLogger(__name__)

class MinioService:
    def __init__(self):
        """
        Inicializa el servicio de MinIO con las credenciales del entorno.
        """
        # Asegurarse de que las variables de entorno estén cargadas
        from dotenv import load_dotenv
        load_dotenv()
        
        # Obtener las variables de entorno
        endpoint_raw = os.getenv("MINIO_ENDPOINT")
        self.access_key = os.getenv("MINIO_ACCESS_KEY")
        self.secret_key = os.getenv("MINIO_SECRET_KEY")
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME")
        self.use_ssl = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
        self.public_url = os.getenv("MINIO_PUBLIC_URL")
        self.endpoint = None  # Inicializar endpoint
        
        # Procesar el endpoint para eliminar el esquema (http:// o https://) y la ruta
        if endpoint_raw:
            # Eliminar el esquema si existe
            if endpoint_raw.startswith("http://"):
                endpoint_raw = endpoint_raw[7:]
            elif endpoint_raw.startswith("https://"):
                endpoint_raw = endpoint_raw[8:]
                
            # Extraer solo el host y el puerto
            host_port = endpoint_raw.split("/")[0]
            
            # Si el endpoint tiene el puerto 9001 (web UI), cambiarlo a 9000 (API S3)
            if host_port.endswith(":9001"):
                host = host_port.split(":")[0]
                self.endpoint = f"{host}:9000"
                logger.warning(f"Cambiando puerto de MinIO de 9001 (web UI) a 9000 (API S3): {self.endpoint}")
            else:
                self.endpoint = host_port

        # Imprimir valores para depuración (sin mostrar la clave secreta completa)
        logger.info(f"MinIO Endpoint: {self.endpoint}")
        logger.info(f"MinIO Access Key: {self.access_key[:4] + '****' if self.access_key else None}")
        logger.info(f"MinIO Secret Key: {'****' + self.secret_key[-4:] if self.secret_key else None}")
        logger.info(f"MinIO Bucket: {self.bucket_name}")
        logger.info(f"MinIO Use SSL: {self.use_ssl}")
        logger.info(f"MinIO Public URL: {self.public_url}")
        
        # Usar valores predeterminados si no están configurados
        if not self.endpoint:
            self.endpoint = "minio-server:9000"
            logger.warning(f"MINIO_ENDPOINT no configurado, usando valor predeterminado: {self.endpoint}")
            
        if not self.bucket_name:
            self.bucket_name = "insectos-images"
            logger.warning(f"MINIO_BUCKET_NAME no configurado, usando valor predeterminado: {self.bucket_name}")
        
        # Verificar credenciales
        if not self.access_key or not self.secret_key:
            logger.error("Credenciales de MinIO no configuradas correctamente")
            raise ValueError("Las credenciales de MinIO son requeridas: MINIO_ACCESS_KEY y MINIO_SECRET_KEY deben estar configuradas en el archivo .env")
        
        # Inicializar cliente de MinIO
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.use_ssl
        )
        
        # Asegurar que el bucket existe
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """
        Verifica si el bucket existe, si no, lo crea.
        """
        try:
            if not self.client.bucket_exists(self.bucket_name):
                region = os.getenv("MINIO_REGION", "us-east-1")
                self.client.make_bucket(self.bucket_name, region)
                logger.info(f"Bucket '{self.bucket_name}' creado exitosamente")
                
                # Configurar política de acceso público (opcional)
                self._set_public_policy()
            else:
                logger.info(f"Bucket '{self.bucket_name}' ya existe")
        except S3Error as e:
            logger.error(f"Error al verificar/crear bucket: {e}")
            raise
    
    def _set_public_policy(self):
        """
        Configura una política de acceso público para el bucket.
        """
        try:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                    }
                ]
            }
            self.client.set_bucket_policy(self.bucket_name, policy)
            logger.info(f"Política de acceso público configurada para '{self.bucket_name}'")
        except S3Error as e:
            logger.warning(f"No se pudo configurar la política de acceso público: {e}")
    
    def _ensure_path_exists(self, path):
        """
        Verifica si el bucket existe. En MinIO, los directorios son virtuales y se crean
        implícitamente al crear objetos con claves que contienen '/'.
        
        No es necesario crear explícitamente los directorios, pero podemos crear un
        objeto vacío con un nombre que termina en '/' para que aparezca como directorio
        en la interfaz de MinIO.
        """
        try:
            # Verificar si el bucket existe
            if not self.client.bucket_exists(self.bucket_name):
                # Crear el bucket si no existe
                self._ensure_bucket_exists()
                
            # Opcionalmente, crear un marcador de directorio vacío
            # Esto no es estrictamente necesario, pero puede ayudar a visualizar la estructura
            # en la interfaz de MinIO
            try:
                logger.info(f"Creando marcador de directorio: {path}/")
                self.client.put_object(self.bucket_name, f"{path}/", b'', 0)
                logger.info(f"Marcador de directorio '{path}/' creado exitosamente")
            except Exception as e:
                # Ignorar errores, ya que esto es solo para visualización
                logger.warning(f"No se pudo crear el marcador de directorio: {e}")
                
        except S3Error as e:
            logger.error(f"Error al verificar/crear bucket: {e}")
            raise
    
    async def upload_image(self, file: UploadFile, path: str = None) -> dict:
        """
        Sube una imagen a MinIO y devuelve la URL.
        
        Args:
            file: El archivo a subir (debe ser una imagen)
            path: Ruta opcional dentro del bucket donde se guardará la imagen
            
        Returns:
            dict: Diccionario con la URL de la imagen y otros metadatos
        """
        try:
            # Crear un archivo temporal
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                # Copiar contenido del archivo subido al temporal
                shutil.copyfileobj(file.file, temp_file)
                temp_file_path = temp_file.name
            
            # Verificar que el archivo es una imagen
            if HAS_MAGIC:
                # Usar python-magic si está disponible
                mime = magic.Magic(mime=True)
                content_type = mime.from_file(temp_file_path)
            else:
                # Alternativa usando mimetypes
                content_type, _ = mimetypes.guess_type(file.filename)
                if not content_type:
                    # Fallback si no se puede determinar el tipo
                    content_type = 'application/octet-stream'
            
            # Verificar que sea una imagen
            if not content_type.startswith('image/'):
                os.unlink(temp_file_path)
                raise ValueError(f"El archivo no es una imagen válida: {content_type}")
            
            # Generar un nombre único para el archivo
            file_extension = os.path.splitext(file.filename)[1]
            
            # Preparar la ruta del objeto
            if path:
                # Normalizar la ruta (eliminar barras iniciales/finales y asegurar formato correcto)
                normalized_path = path.strip('/')
                if normalized_path:
                    # Verificar si la ruta existe
                    self._ensure_path_exists(normalized_path)
                    object_name = f"{normalized_path}/{uuid.uuid4()}{file_extension}"
                else:
                    object_name = f"{uuid.uuid4()}{file_extension}"
            else:
                object_name = f"{uuid.uuid4()}{file_extension}"
            
            logger.info(f"Subiendo imagen a: {object_name}")
            
            # Subir el archivo a MinIO
            self.client.fput_object(
                self.bucket_name, 
                object_name, 
                temp_file_path,
                content_type=content_type
            )
            
            # Eliminar el archivo temporal
            os.unlink(temp_file_path)
            
            # Construir la URL de la imagen
            if self.public_url:
                # URL pública configurada
                image_url = urljoin(self.public_url, f"{self.bucket_name}/{object_name}")
            else:
                # URL generada
                protocol = "https" if self.use_ssl else "http"
                endpoint = self.endpoint.split(':')[0]  # Quitar el puerto si está presente
                port = self.endpoint.split(':')[1] if ':' in self.endpoint else "9000"
                image_url = f"{protocol}://{endpoint}:{port}/{self.bucket_name}/{object_name}"
            
            logger.info(f"Imagen subida exitosamente: {object_name}")
            logger.info(f"URL de la imagen: {image_url}")
            
            # Preparar respuesta con información adicional
            response = {
                "success": True,
                "image_url": image_url,
                "object_name": object_name,
                "content_type": content_type
            }
            
            # Incluir el path si se proporcionó
            if path:
                response["path"] = path
                
            return response
            
        except Exception as e:
            logger.error(f"Error al subir imagen: {e}")
            # Si hay un archivo temporal, eliminarlo
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            raise

# Instancia singleton del servicio
minio_service = MinioService()
