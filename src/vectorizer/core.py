"""Módulo principal de Vectorizer AI."""

import asyncio
import logging
from pathlib import Path
from typing import Callable, Optional

from .vision import VisionAnalyzer
from .svg_generator import SVGGenerator
from .comparator import ImageComparator
from .metrics import MetricsEngine
from .models import (
    VectorizationResult,
    ImageAnalysis,
    SVGGeneration,
    ComparisonResult,
)

logger = logging.getLogger(__name__)


class Vectorizer:
    """Clase principal que orquesta el proceso de vectorización."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_iterations: int = 10,
        quality_threshold: float = 0.85,
        temp_dir: str = "./temp",
        verbose: bool = False,
        provider: str = "anthropic",
        base_url: Optional[str] = None,
    ) -> None:
        """Inicializa el Vectorizer.

        Args:
            api_key: API key para el servicio de IA.
            model: Modelo de IA a usar.
            max_iterations: Número máximo de iteraciones.
            quality_threshold: Umbral de calidad para detener.
            temp_dir: Directorio para archivos temporales.
            verbose: Mostrar información detallada.
            provider: Proveedor de API ("anthropic", "openai", "openrouter", "google").
            base_url: URL base personalizada (para OpenRouter, etc.).
        """
        self.api_key = api_key
        self.model = model
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold
        self.temp_dir = Path(temp_dir)
        self.verbose = verbose
        self.provider = provider
        self.base_url = base_url

        # Crear directorio temporal si no existe
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Inicializar componentes
        self.vision_analyzer = VisionAnalyzer(
            api_key=api_key, model=model, provider=provider, base_url=base_url
        )
        self.svg_generator = SVGGenerator(
            api_key=api_key, model=model, provider=provider, base_url=base_url
        )
        self.image_comparator = ImageComparator()
        self.metrics_engine = MetricsEngine()

        # Configurar logging
        if verbose:
            logging.basicConfig(level=logging.DEBUG)

    def vectorize(
        self,
        input_path: str,
        output_path: str,
        callback: Optional[Callable[[int, float], None]] = None,
    ) -> VectorizationResult:
        """Vectoriza una imagen y guarda el resultado.

        Args:
            input_path: Ruta a la imagen de entrada.
            output_path: Ruta donde guardar el SVG resultante.
            callback: Función llamada en cada iteración con (iteración, calidad).

        Returns:
            VectorizationResult con el resultado de la vectorización.

        Raises:
            FileNotFoundError: Si el archivo de entrada no existe.
            ValueError: Si el formato de imagen no es soportado.
        """
        return asyncio.run(self.vectorize_async(input_path, output_path, callback))

    async def vectorize_async(
        self,
        input_path: str,
        output_path: str,
        callback: Optional[Callable[[int, float], None]] = None,
    ) -> VectorizationResult:
        """Versión asíncrona de vectorize()."""
        # Validar entrada
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")

        logger.info(f"Iniciando vectorizacion de {input_path}")

        # Fase 1: Análisis inicial
        logger.info("Fase 1: Analizando imagen...")
        analysis = await self.vision_analyzer.analyze(str(input_file))
        logger.info(f"Analisis completado: {analysis.description}")

        # Fase 2: Generación inicial
        logger.info("Fase 2: Generando SVG inicial...")
        svg_gen = await self.svg_generator.generate(analysis)
        current_svg = svg_gen.svg_code
        best_svg = current_svg
        best_quality = 0.0

        # Fase 3: Iteraciones de refinamiento
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"Iteracion {iteration}/{self.max_iterations}")

            # Renderizar SVG a PNG
            temp_png = self.temp_dir / f"iteration_{iteration}.png"
            self.image_comparator.render_svg(
                current_svg, str(temp_png), width=1024, height=1024
            )

            # Comparar con original
            comparison = self.image_comparator.compare(str(input_file), str(temp_png))
            quality = comparison.quality_score

            logger.info(f"Calidad actual: {quality:.4f}")

            # Llamar callback si existe
            if callback:
                callback(iteration, quality)

            # Actualizar mejor SVG si mejoró
            if quality > best_quality:
                best_quality = quality
                best_svg = current_svg
                logger.info(f"Nuevo mejor SVG! Calidad: {quality:.4f}")

            # Verificar si alcanzamos el umbral
            if quality >= self.quality_threshold:
                logger.info(f"Umbral de calidad alcanzado: {quality:.4f}")
                break

            # Fase 4: Refinamiento
            logger.info("Refinando SVG...")
            modifications = self._generate_modifications(comparison)
            svg_gen = await self.svg_generator.modify(current_svg, modifications)
            current_svg = svg_gen.svg_code

        # Fase 5: Finalización
        logger.info("Fase 5: Optimizando SVG final...")
        optimized_svg = self.svg_generator.optimize(best_svg, level="medium")

        # Guardar SVG final
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(optimized_svg)

        logger.info(f"SVG guardado en {output_path}")

        # Calcular métricas finales
        final_png = self.temp_dir / "final.png"
        self.image_comparator.render_svg(
            optimized_svg, str(final_png), width=1024, height=1024
        )
        final_comparison = self.image_comparator.compare(
            str(input_file), str(final_png)
        )

        return VectorizationResult(
            svg_code=optimized_svg,
            quality=final_comparison.quality_score,
            iterations=iteration,
            metrics={
                "ssim": final_comparison.ssim,
                "clip_similarity": final_comparison.clip_similarity,
            },
            metadata={
                "input_path": str(input_file),
                "output_path": str(output_file),
                "model": self.model,
                "max_iterations": self.max_iterations,
                "quality_threshold": self.quality_threshold,
                "provider": self.provider,
            },
        )

    def _generate_modifications(self, comparison: ComparisonResult) -> list[str]:
        """Genera lista de modificaciones basadas en la comparación.

        Args:
            comparison: Resultado de la comparación de imágenes.

        Returns:
            Lista de modificaciones a aplicar al SVG.
        """
        modifications = []

        for diff in comparison.differences:
            area = diff.get("area", "")
            issue = diff.get("issue", "")

            if issue == "color_mismatch":
                modifications.append(f"Ajustar colores en el area {area}")
            elif issue == "shape_precision":
                modifications.append(f"Mejorar precision de formas en {area}")
            elif issue == "missing_details":
                modifications.append(f"Agregar detalles faltantes en {area}")
            elif issue == "alignment":
                modifications.append(f"Corregir alineacion en {area}")

        return modifications
