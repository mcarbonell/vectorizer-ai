"""Módulo principal de Vectorizer AI."""

import asyncio
import logging
from pathlib import Path
from typing import Callable, Optional, List, Union
import time

from .vision import VisionAnalyzer
from .svg_generator import SVGGenerator
from .comparator import ImageComparator
from .metrics import MetricsEngine
from .models import (
    VectorizationResult,
    ImageAnalysis,
    SVGGeneration,
    ComparisonResult,
    BatchResult,
)

logger = logging.getLogger(__name__)


class Vectorizer:
    """Clase principal que orchestra el proceso de vectorización."""

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

        Raises:
            ValueError: Si los parámetros son inválidos.
        """
        # Validar parámetros
        if not api_key or not api_key.strip():
            raise ValueError("API key no puede estar vacía")
        
        if max_iterations < 1 or max_iterations > 100:
            raise ValueError("max_iterations debe estar entre 1 y 100")
        
        if not 0.0 <= quality_threshold <= 1.0:
            raise ValueError("quality_threshold debe estar entre 0.0 y 1.0")
        
        if provider not in ["anthropic", "openai", "openrouter", "google"]:
            raise ValueError(f"Proveedor no soportado: {provider}")

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
        
        if not input_file.is_file():
            raise ValueError(f"La ruta no es un archivo: {input_path}")
        
        # Validar formato
        supported_formats = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"]
        if input_file.suffix.lower() not in supported_formats:
            raise ValueError(
                f"Formato no soportado: {input_file.suffix}. "
                f"Formatos soportados: {', '.join(supported_formats)}"
            )
        
        # Validar tamaño de archivo (máximo 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        file_size = input_file.stat().st_size
        if file_size > max_size:
            raise ValueError(
                f"Archivo muy grande: {file_size / 1024 / 1024:.1f}MB. "
                f"Máximo: {max_size / 1024 / 1024:.0f}MB"
            )
        
        # Validar que output_path sea escribible
        output_file = Path(output_path)
        if output_file.exists() and not output_file.is_file():
            raise ValueError(f"La ruta de salida no es un archivo: {output_path}")

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
        render_success = False

        # Fase 3: Iteraciones de refinamiento
        comparison = None
        iteration_history = []  # Historial de iteraciones
        
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"Iteracion {iteration}/{self.max_iterations}")

            # Renderizar SVG a PNG
            try:
                temp_png = self.temp_dir / f"iteration_{iteration}.png"
                self.image_comparator.render_svg(
                    current_svg, str(temp_png), width=1024, height=1024
                )
                render_success = True

                # Comparar con original
                comparison = self.image_comparator.compare(str(input_file), str(temp_png))
                quality = comparison.quality_score

                logger.info(f"Calidad actual: {quality:.4f}")
                
                # Guardar en historial
                iteration_history.append({
                    'iteration': iteration,
                    'quality': quality,
                    'modifications': [],
                })

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

            except RuntimeError as e:
                logger.error(f"Error crítico de renderizado: {e}")
                logger.error("No se puede continuar sin renderizado. Abortando.")
                raise
            except Exception as e:
                logger.warning(f"Error en iteración {iteration}: {e}")
                quality = best_quality

            # Fase 4: Refinamiento con contexto
            logger.info("Refinando SVG...")
            if render_success:
                modifications = self._generate_modifications(comparison)
                # Agregar contexto de intentos previos
                context = {
                    'previous_attempts': [h.get('modifications', []) for h in iteration_history[-3:]],
                    'best_quality': best_quality,
                    'current_quality': quality,
                }
            else:
                modifications = ["Mejorar la representación SVG"]
                context = {}
            
            # Guardar modificaciones en historial
            if iteration_history:
                iteration_history[-1]['modifications'] = modifications
            
            svg_gen = await self.svg_generator.modify(current_svg, modifications, context)
            current_svg = svg_gen.svg_code

        # Fase 5: Finalización - GUARDAR SVG SIEMPRE
        logger.info("Fase 5: Optimizando y guardando SVG...")

        # Optimizar SVG
        optimized_svg = self.svg_generator.optimize(best_svg, level="medium")

        # Guardar SVG final
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(optimized_svg)
        logger.info(f"SVG guardado en {output_path}")

        # Calcular métricas si el renderizado fue exitoso
        try:
            final_png = self.temp_dir / "final.png"
            self.image_comparator.render_svg(
                optimized_svg, str(final_png), width=1024, height=1024
            )
            final_comparison = self.image_comparator.compare(
                str(input_file), str(final_png)
            )
            final_quality = final_comparison.quality_score
        except Exception:
            final_quality = best_quality

        return VectorizationResult(
            svg_code=optimized_svg,
            quality=final_quality,
            iterations=iteration,
            metrics={
                "ssim": getattr(final_comparison, 'ssim', 0.0) if 'final_comparison' in dir() else 0.0,
                "clip_similarity": getattr(final_comparison, 'clip_similarity', 0.0) if 'final_comparison' in dir() else 0.0,
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

    def vectorize_batch(
        self,
        input_paths: Union[List[str], str],
        output_dir: str,
        callback: Optional[Callable[[str, int, int, float], None]] = None,
        continue_on_error: bool = True,
        parallel: bool = False,
        max_workers: int = 3,
    ) -> BatchResult:
        """Vectoriza múltiples imágenes en modo batch.

        Args:
            input_paths: Lista de rutas de imágenes o patrón glob (ej: "images/*.png").
            output_dir: Directorio donde guardar los SVGs resultantes.
            callback: Función llamada con (filename, current, total, quality).
            continue_on_error: Continuar procesando si una imagen falla.
            parallel: Procesar imágenes en paralelo (experimental).
            max_workers: Número máximo de workers paralelos.

        Returns:
            BatchResult con estadísticas del procesamiento.

        Raises:
            ValueError: Si input_paths está vacío o output_dir es inválido.
        """
        return asyncio.run(
            self.vectorize_batch_async(
                input_paths, output_dir, callback, continue_on_error, parallel, max_workers
            )
        )

    async def vectorize_batch_async(
        self,
        input_paths: Union[List[str], str],
        output_dir: str,
        callback: Optional[Callable[[str, int, int, float], None]] = None,
        continue_on_error: bool = True,
        parallel: bool = False,
        max_workers: int = 3,
    ) -> BatchResult:
        """Versión asíncrona de vectorize_batch()."""
        start_time = time.time()
        
        # Resolver input_paths
        if isinstance(input_paths, str):
            # Patrón glob
            from glob import glob
            resolved_paths = glob(input_paths, recursive=True)
            if not resolved_paths:
                raise ValueError(f"No se encontraron archivos con el patrón: {input_paths}")
        else:
            resolved_paths = input_paths
        
        if not resolved_paths:
            raise ValueError("input_paths no puede estar vacío")
        
        # Validar output_dir
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if not output_path.is_dir():
            raise ValueError(f"output_dir no es un directorio válido: {output_dir}")
        
        logger.info(f"Iniciando procesamiento batch de {len(resolved_paths)} imágenes")
        
        results = []
        errors = []
        successful = 0
        failed = 0
        
        # Procesar imágenes
        if parallel:
            # Modo paralelo (experimental)
            tasks = []
            for idx, input_file in enumerate(resolved_paths, 1):
                task = self._process_single_image(
                    input_file, output_path, idx, len(resolved_paths), 
                    callback, continue_on_error
                )
                tasks.append(task)
            
            # Limitar concurrencia
            semaphore = asyncio.Semaphore(max_workers)
            
            async def bounded_task(task):
                async with semaphore:
                    return await task
            
            batch_results = await asyncio.gather(
                *[bounded_task(task) for task in tasks],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, Exception):
                    failed += 1
                    errors.append({
                        "file": "unknown",
                        "error": str(result)
                    })
                elif result.get("success"):
                    successful += 1
                    results.append(result)
                else:
                    failed += 1
                    errors.append(result.get("error", {}))
        else:
            # Modo secuencial
            for idx, input_file in enumerate(resolved_paths, 1):
                result = await self._process_single_image(
                    input_file, output_path, idx, len(resolved_paths),
                    callback, continue_on_error
                )
                
                if result.get("success"):
                    successful += 1
                    results.append(result)
                else:
                    failed += 1
                    errors.append(result.get("error", {}))
        
        elapsed_time = time.time() - start_time
        
        logger.info(
            f"Procesamiento batch completado: {successful} exitosos, "
            f"{failed} fallidos en {elapsed_time:.2f}s"
        )
        
        return BatchResult(
            total=len(resolved_paths),
            successful=successful,
            failed=failed,
            results=results,
            errors=errors,
            metadata={
                "elapsed_time": elapsed_time,
                "parallel": parallel,
                "max_workers": max_workers if parallel else 1,
                "output_dir": str(output_path),
            }
        )

    async def _process_single_image(
        self,
        input_file: str,
        output_dir: Path,
        current: int,
        total: int,
        callback: Optional[Callable[[str, int, int, float], None]],
        continue_on_error: bool,
    ) -> dict:
        """Procesa una sola imagen en modo batch.

        Args:
            input_file: Ruta de la imagen de entrada.
            output_dir: Directorio de salida.
            current: Índice actual (1-based).
            total: Total de imágenes.
            callback: Callback opcional.
            continue_on_error: Continuar si falla.

        Returns:
            Diccionario con resultado o error.
        """
        input_path = Path(input_file)
        filename = input_path.stem
        output_file = output_dir / f"{filename}.svg"
        
        logger.info(f"[{current}/{total}] Procesando: {input_path.name}")
        
        try:
            # Vectorizar imagen
            result = await self.vectorize_async(
                str(input_path),
                str(output_file),
                callback=lambda iter, qual: callback(
                    input_path.name, current, total, qual
                ) if callback else None
            )
            
            logger.info(
                f"[{current}/{total}] ✓ {input_path.name} - "
                f"Calidad: {result.quality:.4f}, Iteraciones: {result.iterations}"
            )
            
            return {
                "success": True,
                "input": str(input_path),
                "output": str(output_file),
                "filename": input_path.name,
                "quality": result.quality,
                "iterations": result.iterations,
                "metrics": result.metrics,
            }
            
        except Exception as e:
            logger.error(f"[{current}/{total}] ✗ {input_path.name} - Error: {e}")
            
            if not continue_on_error:
                raise
            
            return {
                "success": False,
                "error": {
                    "file": str(input_path),
                    "filename": input_path.name,
                    "error": str(e),
                    "type": type(e).__name__,
                }
            }
