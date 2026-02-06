"""Módulo de análisis de visión para Vectorizer AI."""

import base64
import logging
from pathlib import Path
from typing import Optional

import anthropic
from openai import OpenAI
from PIL import Image
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .local_llm import create_local_client
from .models import ImageAnalysis

logger = logging.getLogger(__name__)


class VisionAnalyzer:
    """Analiza imágenes usando APIs de visión."""

    SUPPORTED_PROVIDERS = [
        "anthropic",
        "openai",
        "openrouter",
        "google",
        "ollama",
        "lmstudio",
    ]

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        provider: str = "anthropic",
        base_url: Optional[str] = None,
        enable_cache: bool = True,
        cache_ttl: int = 3600,
    ) -> None:
        """Inicializa el VisionAnalyzer.

        Args:
            api_key: API key para el servicio de IA.
            model: Modelo de IA a usar.
            provider: Proveedor de API ("anthropic", "openai", "openrouter", "google").
            base_url: URL base personalizada (útil para OpenRouter, LM Studio, etc.).
            enable_cache: Habilitar caché de respuestas.
            cache_ttl: Tiempo de vida del caché en segundos.
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.base_url = base_url
        self.enable_cache = enable_cache

        # Inicializar caché
        if enable_cache:
            from .cache import CacheManager

            self.cache = CacheManager(cache_dir=".cache/vision", ttl=cache_ttl)
        else:
            self.cache = None

        if provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=api_key)
        elif provider in ["openai", "openrouter"]:
            # OpenRouter es compatible con OpenAI
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url or "https://openrouter.ai/api/v1",
            )
        elif provider == "google":
            # Google Gemini usa la nueva API google.genai
            try:
                from google import genai

                self.client = genai.Client(api_key=api_key)
                self._using_new_google_api = True
            except ImportError:
                # Fallback a la API anterior
                import google.generativeai as genai

                genai.configure(api_key=api_key)
                self.client = genai
                self._using_new_google_api = False
        elif provider in ["ollama", "lmstudio"]:
            # LLMs locales (Ollama y LM Studio)
            self.client = create_local_client(
                provider=provider,
                model=model,
                base_url=base_url,
                timeout=120,
            )
        else:
            raise ValueError(f"Proveedor no soportado: {provider}")

    async def analyze(
        self, image_path: str, detail_level: str = "medium"
    ) -> ImageAnalysis:
        """Analiza una imagen y extrae características visuales.

        Args:
            image_path: Ruta a la imagen a analizar.
            detail_level: Nivel de detalle ("low", "medium", "high").

        Returns:
            ImageAnalysis con las características extraídas.

        Raises:
            FileNotFoundError: Si el archivo no existe.
            ValueError: Si el formato de imagen no es soportado.
        """
        image_file = Path(image_path)
        if not image_file.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {image_path}")

        # Verificar caché
        if self.cache:
            import hashlib

            with open(image_file, "rb") as f:
                image_hash = hashlib.md5(f.read()).hexdigest()
            cache_key = self.cache.get_cache_key(image_hash, self.model, detail_level)
            cached = self.cache.get(cache_key)
            if cached:
                logger.info(f"Usando análisis cacheado para {image_path}")
                return ImageAnalysis(**cached)

        logger.info(f"Analizando imagen: {image_path}")

        # Leer imagen
        image_data = self._encode_image(image_file)

        # Crear prompt para análisis
        prompt = self._create_analysis_prompt(detail_level)

        # Llamar a la API según el proveedor
        if self.provider == "anthropic":
            response = await self._call_anthropic(image_data, prompt)
        elif self.provider in ["openai", "openrouter"]:
            response = await self._call_openai(image_data, prompt)
        elif self.provider == "google":
            response = await self._call_google(image_file, prompt)
        elif self.provider in ["ollama", "lmstudio"]:
            response = await self._call_local(image_file, prompt)
            # Guardar en caché
            if self.cache:
                self.cache.set(cache_key, response.__dict__)
            return response

        # Parsear respuesta (si no es ya un ImageAnalysis)
        if isinstance(response, ImageAnalysis):
            result = response
        else:
            result = self._parse_analysis_response(response)

        # Guardar en caché
        if self.cache:
            self.cache.set(cache_key, result.__dict__)

        return result

    def _encode_image(self, image_path: Path) -> tuple[str, str, Image.Image]:
        """Codifica una imagen.

        Args:
            image_path: Ruta a la imagen.

        Returns:
            Tupla (media_type, base64_data, pil_image).
        """
        media_type = self._get_media_type(image_path.suffix)

        # Cargar como PIL Image para Google API
        pil_image = Image.open(image_path)

        with open(image_path, "rb") as f:
            base64_data = base64.b64encode(f.read()).decode("utf-8")

        return media_type, base64_data, pil_image

    def _get_media_type(self, extension: str) -> str:
        """Obtiene el tipo MIME basado en la extensión.

        Args:
            extension: Extensión del archivo (ej: ".png").

        Returns:
            Tipo MIME.
        """
        media_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
        }

        media_type = media_types.get(extension.lower())
        if not media_type:
            raise ValueError(f"Formato no soportado: {extension}")

        return media_type

    def _create_analysis_prompt(self, detail_level: str) -> str:
        """Crea el prompt para análisis de imagen.

        Args:
            detail_level: Nivel de detalle.

        Returns:
            Prompt para la API.
        """
        from .prompts import get_analysis_prompt

        # Usar prompt mejorado con few-shot
        return get_analysis_prompt(
            description="imagen a analizar", colors=[], shapes=[], style=""
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    async def _call_anthropic(
        self, image_data: tuple[str, str, Image.Image], prompt: str
    ) -> str:
        """Llama a la API de Anthropic con reintentos.

        Args:
            image_data: Tupla (media_type, base64_data, pil_image).
            prompt: Prompt para la API.

        Returns:
            Respuesta de la API.

        Raises:
            ConnectionError: Si falla la conexión después de reintentos.
        """
        media_type, base64_data, _ = image_data

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": base64_data,
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Error llamando a Anthropic: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    async def _call_openai(
        self, image_data: tuple[str, str, Image.Image], prompt: str
    ) -> str:
        """Llama a la API de OpenAI o OpenRouter con reintentos.

        Args:
            image_data: Tupla (media_type, base64_data, pil_image).
            prompt: Prompt para la API.

        Returns:
            Respuesta de la API.

        Raises:
            ConnectionError: Si falla la conexión después de reintentos.
        """
        media_type, base64_data, _ = image_data

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{base64_data}"
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                max_tokens=1024,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error llamando a OpenAI: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    async def _call_google(self, image_path: Path, prompt: str) -> ImageAnalysis:
        """Llama a la API de Google Gemini con reintentos.

        Args:
            image_path: Ruta a la imagen.
            prompt: Prompt para la API.

        Returns:
            ImageAnalysis con los datos.

        Raises:
            ConnectionError: Si falla la conexión después de reintentos.
        """
        pil_image = Image.open(image_path)

        try:
            if getattr(self, "_using_new_google_api", False):
                from google import genai

                client: genai.Client = self.client

                response = client.models.generate_content(
                    model=self.model,
                    contents=[prompt, pil_image],
                )

                return self._parse_analysis_response(response.text)
            else:
                import google.generativeai as genai

                model = genai.GenerativeModel(self.model)

                response = model.generate_content([prompt, pil_image])

                return self._parse_analysis_response(response.text)
        except Exception as e:
            logger.error(f"Error llamando a Google: {e}")
            raise

    async def _call_local(self, image_path: Path, prompt: str) -> ImageAnalysis:
        """Llama a un LLM local (Ollama o LM Studio) con reintentos.

        Args:
            image_path: Ruta a la imagen.
            prompt: Prompt para la API.

        Returns:
            ImageAnalysis con los datos.

        Raises:
            ConnectionError: Si falla la conexión después de reintentos.
        """
        try:
            response = self.client.vision_completion(
                image_path=str(image_path),
                prompt=prompt,
                max_tokens=1024,
            )
            return self._parse_analysis_response(response)
        except Exception as e:
            logger.error(f"Error llamando a LLM local ({self.provider}): {e}")
            raise

    def _parse_analysis_response(self, response: str) -> ImageAnalysis:
        """Parsea la respuesta de la API.

        Args:
            response: Respuesta de la API en formato JSON.

        Returns:
            ImageAnalysis con los datos parseados.
        """
        import json

        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            # Si la respuesta no es JSON válido, intentar extraer JSON
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                # Fallback a valores por defecto
                logger.warning("No se pudo parsear la respuesta como JSON")
                data = {
                    "shapes": [],
                    "colors": [],
                    "composition": "desconocida",
                    "complexity": "media",
                    "style": "desconocido",
                    "description": response[:200],
                }

        return ImageAnalysis(
            shapes=data.get("shapes", []),
            colors=data.get("colors", []),
            composition=data.get("composition", "desconocida"),
            complexity=data.get("complexity", "media"),
            style=data.get("style", "desconocido"),
            description=data.get("description", ""),
        )
