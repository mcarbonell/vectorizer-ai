"""Módulo de generación de SVG para Vectorizer AI."""

import logging
import re
from typing import List

import anthropic
from openai import OpenAI

from .models import ImageAnalysis, SVGGeneration

logger = logging.getLogger(__name__)


class SVGGenerator:
    """Genera y modifica código SVG."""

    def __init__(
        self, api_key: str, model: str = "claude-3-5-sonnet-20241022"
    ) -> None:
        """Inicializa el SVGGenerator.

        Args:
            api_key: API key para el servicio de IA.
            model: Modelo de IA a usar.
        """
        self.api_key = api_key
        self.model = model

        # Inicializar clientes (usar Anthropic por defecto)
        self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        self.openai_client = OpenAI(api_key=api_key)

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
        svg_code = self._extract_svg(response)

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
        modified_svg = self._extract_svg(response)

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
Formas principales: {', '.join(analysis.shapes)}
Colores principales: {', '.join(analysis.colors)}
Composición: {analysis.composition}
Complejidad: {analysis.complexity}
Estilo: {style}

Requisitos:
1. El SVG debe ser válido y bien formado
2. Usa solo los colores especificados
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
        """Llama a la API de Anthropic.

        Args:
            prompt: Prompt para la API.

        Returns:
            Respuesta de la API.
        """
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

    def _extract_svg(self, response: str) -> str:
        """Extrae el código SVG de la respuesta.

        Args:
            response: Respuesta de la API.

        Returns:
            Código SVG extraído.
        """
        # Buscar etiquetas SVG
        svg_match = re.search(r"<svg[^>]*>.*?</svg>", response, re.DOTALL)

        if svg_match:
            return svg_match.group(0)

        # Si no se encuentra, intentar con etiquetas sin cierre
        svg_match = re.search(r"<svg[^>]*/>", response)

        if svg_match:
            return svg_match.group(0)

        # Si no se encuentra, retornar la respuesta completa
        logger.warning("No se encontró etiqueta SVG en la respuesta")
        return response

    def _validate_svg(self, svg_code: str) -> bool:
        """Valida que el código SVG sea válido.

        Args:
            svg_code: Código SVG a validar.

        Returns:
            True si es válido, False en caso contrario.
        """
        # Verificar que tenga etiqueta SVG
        if not re.search(r"<svg[^>]*>", svg_code):
            return False

        # Verificar que tenga cierre
        if not re.search(r"</svg>", svg_code) and not re.search(
            r"<svg[^>]*/>", svg_code
        ):
            return False

        # Verificar que tenga xmlns
        if 'xmlns="http://www.w3.org/2000/svg"' not in svg_code:
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
        color = analysis.colors[0] if analysis.colors else "#000000"

        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="{color}"/>
</svg>"""
