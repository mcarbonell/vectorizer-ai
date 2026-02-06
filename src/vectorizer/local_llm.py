"""Cliente de LLM local para Ollama y LM Studio.

Este módulo proporciona soporte para LLMs locales mediante:
- Ollama (http://localhost:11434)
- LM Studio (http://localhost:1234)

Ambos usan la API compatible con OpenAI, lo que facilita la integración.
"""

import base64
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


class LocalLLMClient:
    """Cliente base para LLMs locales (Ollama y LM Studio).

    Ambos proveedores usan la API compatible con OpenAI, lo que permite
    reutilizar el mismo código con diferentes URLs base.
    """

    # URLs por defecto para cada proveedor
    DEFAULT_URLS = {
        "ollama": "http://localhost:11434/v1",
        "lmstudio": "http://localhost:1234/v1",
    }

    def __init__(
        self,
        provider: str,
        model: str = "llava",
        base_url: Optional[str] = None,
        timeout: int = 120,
    ) -> None:
        """Inicializa el cliente de LLM local.

        Args:
            provider: Proveedor local ("ollama" o "lmstudio").
            base_url: URL base personalizada (opcional).
            model: Modelo a usar (ej: "llava", "llama3.2-vision").
            timeout: Timeout en segundos para las peticiones.

        Raises:
            ValueError: Si el proveedor no es soportado.
        """
        if provider not in self.DEFAULT_URLS:
            raise ValueError(
                f"Proveedor local no soportado: {provider}. "
                f"Proveedores soportados: {list(self.DEFAULT_URLS.keys())}"
            )

        self.provider = provider
        self.model = model
        self.timeout = timeout
        self.base_url = base_url or self.DEFAULT_URLS[provider]

        logger.info(f"Inicializando cliente {provider} en {self.base_url}")

        # Inicializar cliente OpenAI (compatible con Ollama y LM Studio)
        self.client = OpenAI(
            base_url=self.base_url,
            api_key="not-needed",  # Ollama y LM Studio no requieren API key
            timeout=timeout,
        )

    def test_connection(self) -> bool:
        """Prueba la conexión con el LLM local.

        Returns:
            True si la conexión es exitosa, False en caso contrario.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            return response.choices[0].message.content is not None
        except Exception as e:
            logger.error(f"Error probando conexión con {self.provider}: {e}")
            return False

    def list_models(self) -> List[str]:
        """Lista los modelos disponibles en el LLM local.

        Returns:
            Lista de nombres de modelos disponibles.
        """
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Error listando modelos: {e}")
            return []

    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Genera una respuesta de chat.

        Args:
            messages: Lista de mensajes (role, content).
            max_tokens: Máximo de tokens a generar.
            temperature: Temperatura para la generación.

        Returns:
            Respuesta del modelo como texto.

        Raises:
            RuntimeError: Si hay un error en la petición.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Error en chat completion: {e}")
            raise RuntimeError(f"Error en chat completion: {e}")

    def _get_media_type(self, extension: str) -> str:
        """Obtiene el tipo MIME basado en la extensión.

        Args:
            extension: Extensión del archivo (ej: ".png").

        Returns:
            Tipo MIME.

        Raises:
            ValueError: Si el formato no es soportado.
        """
        media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
        }

        extension = extension.lower()
        if extension not in media_types:
            raise ValueError(f"Formato de imagen no soportado: {extension}")

        return media_types[extension]

    def vision_completion(
        self,
        image_path: str,
        prompt: str,
        max_tokens: int = 1024,
        detail: str = "auto",
    ) -> str:
        """Realiza una petición de visión con imagen.

        Args:
            image_path: Ruta a la imagen.
            prompt: Prompt para el análisis.
            max_tokens: Máximo de tokens a generar.
            detail: Nivel de detalle ("low", "auto", "high").

        Returns:
            Respuesta del modelo como texto.

        Raises:
            FileNotFoundError: Si la imagen no existe.
            RuntimeError: Si hay un error en la petición.
        """
        image_file = Path(image_path)
        if not image_file.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {image_path}")

        # Leer y codificar la imagen en base64
        with open(image_file, "rb") as f:
            image_data = f.read()

        base64_data = base64.b64encode(image_data).decode("utf-8")
        media_type = self._get_media_type(image_file.suffix)

        # Crear mensaje con imagen (formato OpenAI vision)
        image_url = f"data:{media_type};base64,{base64_data}"

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                            "detail": detail,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Error en vision completion: {e}")
            raise RuntimeError(f"Error en vision completion: {e}")


class OllamaClient(LocalLLMClient):
    """Cliente específico para Ollama."""

    def __init__(
        self,
        model: str = "llava",
        base_url: Optional[str] = None,
        timeout: int = 120,
    ) -> None:
        """Inicializa el cliente de Ollama.

        Args:
            model: Modelo a usar (ej: "llava", "llama3.2-vision").
            base_url: URL base personalizada.
            timeout: Timeout en segundos.
        """
        super().__init__(
            provider="ollama",
            model=model,
            base_url=base_url,
            timeout=timeout,
        )


class LMStudioClient(LocalLLMClient):
    """Cliente específico para LM Studio."""

    def __init__(
        self,
        model: str = "llava-1.5-7b",
        base_url: Optional[str] = None,
        timeout: int = 120,
    ) -> None:
        """Inicializa el cliente de LM Studio.

        Args:
            model: Modelo a usar.
            base_url: URL base personalizada.
            timeout: Timeout en segundos.
        """
        super().__init__(
            provider="lmstudio",
            model=model,
            base_url=base_url,
            timeout=timeout,
        )


def create_local_client(
    provider: str,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: int = 120,
) -> LocalLLMClient:
    """Factory function para crear clientes de LLMs locales.

    Args:
        provider: Proveedor ("ollama" o "lmstudio").
        model: Modelo a usar (opcional, se usa el por defecto del proveedor).
        base_url: URL base personalizada.
        timeout: Timeout en segundos.

    Returns:
        Instancia del cliente apropiado.

    Raises:
        ValueError: Si el proveedor no es soportado.
    """
    if provider == "ollama":
        return OllamaClient(model=model or "llava", base_url=base_url, timeout=timeout)
    elif provider == "lmstudio":
        return LMStudioClient(
            model=model or "llava-1.5-7b", base_url=base_url, timeout=timeout
        )
    else:
        raise ValueError(f"Proveedor local no soportado: {provider}")
