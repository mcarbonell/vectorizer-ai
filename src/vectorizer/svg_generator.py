"""Módulo de generación de SVG para Vectorizer AI."""

import logging
import re
from typing import List, Optional

import anthropic
from openai import OpenAI
from PIL import Image
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .models import ImageAnalysis, SVGGeneration

logger = logging.getLogger(__name__)


class SVGGenerator:
    """Genera y modifica código SVG."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        provider: str = "anthropic",
        base_url: Optional[str] = None,
    ) -> None:
        """Inicializa el SVGGenerator.

        Args:
            api_key: API key para el servicio de IA.
            model: Modelo de IA a usar.
            provider: Proveedor de API ("anthropic", "openai", "openrouter", "google").
            base_url: URL base personalizada.
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.base_url = base_url

        # Inicializar clientes según el proveedor
        self.anthropic_client = None
        self.openai_client = None
        self.google_client = None

        if provider == "anthropic":
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        elif provider in ["openai", "openrouter"]:
            self.openai_client = OpenAI(
                api_key=api_key,
                base_url=base_url or "https://openrouter.ai/api/v1",
            )
        elif provider == "google":
            # Usar la nueva API google.genai
            try:
                from google import genai

                self.google_client = genai.Client(api_key=api_key)
                self._using_new_google_api = True
            except ImportError:
                # Fallback a la API anterior
                import google.generativeai as genai

                genai.configure(api_key=api_key)
                self.google_client = genai
                self._using_new_google_api = False

    async def generate(
        self, analysis: ImageAnalysis, style: str = "flat"
    ) -> SVGGeneration:
        """Genera un SVG basado en el análisis de una imagen.

        Args:
            analysis: Análisis de la imagen.
            style: Estilo del SVG ("flat", "outline", "detailed").

        Returns:
            SVGGeneration con el SVG generado.
        """
        logger.info("Generando SVG inicial...")

        # Crear prompt para generación
        prompt = self._create_generation_prompt(analysis, style)

        # Llamar a la API
        response = await self._call_api(prompt)

        # Extraer SVG de la respuesta
        try:
            svg_code = self._extract_svg(response)
        except ValueError as e:
            logger.error(f"Error extrayendo SVG: {e}")
            logger.info("Usando SVG fallback")
            svg_code = self._create_fallback_svg(analysis)

        # Validar SVG
        if not self._validate_svg(svg_code):
            logger.warning("SVG generado no es válido, usando fallback")
            svg_code = self._create_fallback_svg(analysis)

        return SVGGeneration(
            svg_code=svg_code,
            metadata={
                "style": style,
                "shapes_count": len(analysis.shapes),
                "colors_count": len(analysis.colors),
            },
            iteration=0,
        )

    async def modify(
        self, svg_code: str, modifications: List[str]
    ) -> SVGGeneration:
        """Modifica un SVG existente según las instrucciones.

        Args:
            svg_code: Código SVG a modificar.
            modifications: Lista de modificaciones a aplicar.

        Returns:
            SVGGeneration con el SVG modificado.
        """
        logger.info(f"Modificando SVG con {len(modifications)} cambios...")

        # Crear prompt para modificación
        prompt = self._create_modification_prompt(svg_code, modifications)

        # Llamar a la API
        response = await self._call_api(prompt)

        # Extraer SVG de la respuesta
        try:
            modified_svg = self._extract_svg(response)
        except ValueError as e:
            logger.error(f"Error extrayendo SVG modificado: {e}")
            logger.warning("Retornando SVG original sin modificar")
            return SVGGeneration(
                svg_code=svg_code,
                metadata={"modifications_applied": 0, "error": str(e)},
            )

        # Validar SVG
        if not self._validate_svg(modified_svg):
            logger.warning("SVG modificado no es válido, retornando original")
            modified_svg = svg_code

        return SVGGeneration(
            svg_code=modified_svg,
            metadata={"modifications_applied": len(modifications)},
        )

    def optimize(self, svg_code: str, level: str = "medium") -> str:
        """Optimiza el código SVG reduciendo su tamaño.

        Args:
            svg_code: Código SVG a optimizar.
            level: Nivel de optimización ("low", "medium", "high").

        Returns:
            Código SVG optimizado.
        """
        logger.info(f"Optimizando SVG (nivel: {level})...")

        optimized = svg_code

        # Eliminar comentarios
        optimized = re.sub(r"<!--.*?-->", "", optimized, flags=re.DOTALL)

        # Eliminar espacios en blanco extra
        if level in ["medium", "high"]:
            optimized = re.sub(r">\s+<", "><", optimized)
            optimized = re.sub(r"\s+", " ", optimized)

        # Eliminar atributos por defecto
        if level == "high":
            optimized = re.sub(r' fill="none"', "", optimized)
            optimized = re.sub(r' stroke="none"', "", optimized)
            optimized = re.sub(r' stroke-width="1"', "", optimized)

        # Reducir precisión de números
        if level == "high":
            optimized = re.sub(r"(\d+\.\d{3})\d+", r"\1", optimized)

        return optimized.strip()

    def _create_generation_prompt(
        self, analysis: ImageAnalysis, style: str
    ) -> str:
        """Crea el prompt para generación de SVG.

        Args:
            analysis: Análisis de la imagen.
            style: Estilo deseado.

        Returns:
            Prompt para la API.
        """
        prompt = f"""Genera un código SVG que represente la siguiente imagen:

Descripción: {analysis.description}
Formas principales: {', '.join(analysis.shapes) if analysis.shapes else 'No específicas'}
Colores principales: {', '.join(analysis.colors) if analysis.colors else 'No específicos'}
Composición: {analysis.composition}
Complejidad: {analysis.complexity}
Estilo: {style}

Requisitos:
1. El SVG debe ser válido y bien formado
2. Usa solo los colores especificados o colores similares
3. Mantén la composición descrita
4. El SVG debe ser responsive (viewBox)
5. No incluyas texto o comentarios en el SVG
6. Devuelve SOLO el código SVG, sin explicaciones adicionales

Ejemplo de formato:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- contenido del SVG -->
</svg>
"""
        return prompt

    def _create_modification_prompt(
        self, svg_code: str, modifications: List[str]
    ) -> str:
        """Crea el prompt para modificación de SVG.

        Args:
            svg_code: Código SVG actual.
            modifications: Lista de modificaciones.

        Returns:
            Prompt para la API.
        """
        modifications_text = "\n".join(
            f"- {mod}" for mod in modifications
        )

        prompt = f"""Modifica el siguiente código SVG aplicando estos cambios:

{modifications_text}

SVG actual:
{svg_code}

Requisitos:
1. Aplica solo las modificaciones solicitadas
2. Mantén el resto del SVG sin cambios
3. El SVG resultante debe ser válido
4. Devuelve SOLO el código SVG modificado, sin explicaciones
"""
        return prompt

    async def _call_api(self, prompt: str) -> str:
        """Llama a la API según el proveedor configurado.

        Args:
            prompt: Prompt para la API.

        Returns:
            Respuesta de la API.
        """
        if self.provider == "anthropic":
            return await self._call_anthropic(prompt)
        elif self.provider in ["openai", "openrouter"]:
            return await self._call_openai(prompt)
        elif self.provider == "google":
            return await self._call_google(prompt)
        else:
            # Default to anthropic
            return await self._call_anthropic(prompt)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    async def _call_anthropic(self, prompt: str) -> str:
        """Llama a la API de Anthropic con reintentos.

        Args:
            prompt: Prompt para la API.

        Returns:
            Respuesta de la API.
        """
        try:
            message = self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Error en Anthropic API: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    async def _call_openai(self, prompt: str) -> str:
        """Llama a la API de OpenAI o OpenRouter con reintentos.

        Args:
            prompt: Prompt para la API.

        Returns:
            Respuesta de la API.
        """
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error en OpenAI API: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    async def _call_google(self, prompt: str) -> str:
        """Llama a la API de Google Gemini con reintentos.

        Args:
            prompt: Prompt para la API.

        Returns:
            Respuesta de la API.
        """
        try:
            if getattr(self, "_using_new_google_api", False):
                from google import genai

                client: genai.Client = self.google_client

                response = client.models.generate_content(
                    model=self.model,
                    contents=[prompt],
                )

                return response.text
            else:
                import google.generativeai as genai

                model = genai.GenerativeModel(self.model)

                response = model.generate_content([prompt])

                return response.text
        except Exception as e:
            logger.error(f"Error en Google API: {e}")
            raise

    def _extract_svg(self, response: str) -> str:
        """Extrae el código SVG de la respuesta.

        Args:
            response: Respuesta de la API.

        Returns:
            Código SVG extraído.

        Raises:
            ValueError: Si no se puede extraer SVG válido.
        """
        # Método 1: Markdown code block
        if "```" in response:
            # Buscar ```svg o ```xml
            for lang in ["svg", "xml", ""]:
                pattern = rf"```{lang}\s*\n(.*?)\n```"
                match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
                if match:
                    svg_code = match.group(1).strip()
                    if "<svg" in svg_code:
                        logger.debug(f"SVG extraído de markdown code block ({lang})")
                        return svg_code

        # Método 2: Etiquetas SVG completas
        svg_match = re.search(r"<svg[^>]*>.*?</svg>", response, re.DOTALL | re.IGNORECASE)
        if svg_match:
            logger.debug("SVG extraído con regex estándar")
            return svg_match.group(0)

        # Método 3: SVG auto-cerrado
        svg_match = re.search(r"<svg[^>]*/>", response, re.IGNORECASE)
        if svg_match:
            logger.debug("SVG auto-cerrado extraído")
            return svg_match.group(0)

        # Método 4: Buscar inicio y fin manualmente
        if "<svg" in response.lower() and "</svg>" in response.lower():
            start = response.lower().find("<svg")
            end = response.lower().find("</svg>", start) + 6
            if start != -1 and end > start:
                svg_code = response[start:end]
                logger.debug("SVG extraído con búsqueda manual")
                return svg_code

        # Sin SVG encontrado
        logger.error("No se pudo extraer SVG de la respuesta")
        logger.debug(f"Respuesta recibida: {response[:200]}...")
        raise ValueError(
            "No se encontró código SVG válido en la respuesta. "
            "La IA debe devolver código SVG entre etiquetas <svg>...</svg>"
        )

    def _validate_svg(self, svg_code: str) -> bool:
        """Valida que el código SVG sea válido.

        Args:
            svg_code: Código SVG a validar.

        Returns:
            True si es válido, False en caso contrario.
        """
        if not svg_code or not svg_code.strip():
            logger.warning("SVG vacío")
            return False

        # Verificar etiqueta SVG de apertura
        if not re.search(r"<svg[^>]*>", svg_code, re.IGNORECASE):
            logger.warning("No tiene etiqueta <svg>")
            return False

        # Verificar cierre (</svg> o auto-cerrado)
        has_closing = re.search(r"</svg>", svg_code, re.IGNORECASE)
        has_self_closing = re.search(r"<svg[^>]*/>", svg_code, re.IGNORECASE)
        
        if not has_closing and not has_self_closing:
            logger.warning("SVG sin cierre")
            return False

        # Verificar xmlns (requerido para SVG válido)
        if 'xmlns="http://www.w3.org/2000/svg"' not in svg_code:
            logger.warning("SVG sin xmlns (se puede agregar)")
            # No es crítico, muchos navegadores lo aceptan

        # Verificar que tenga contenido (no solo etiqueta vacía)
        if has_self_closing:
            # SVG auto-cerrado sin contenido
            logger.warning("SVG auto-cerrado sin contenido")
            return False

        return True

    def _create_fallback_svg(self, analysis: ImageAnalysis) -> str:
        """Crea un SVG simple como fallback.

        Args:
            analysis: Análisis de la imagen.

        Returns:
            Código SVG simple.
        """
        # Usar el primer color disponible o un color por defecto
        color = (
            analysis.colors[0] if analysis.colors else "#000000"
        )

        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="{color}"/>
</svg>'''
