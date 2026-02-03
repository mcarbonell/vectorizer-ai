"""Módulo de comparación de imágenes para Vectorizer AI."""

import logging
from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image

from .models import ComparisonResult

logger = logging.getLogger(__name__)


class ImageComparator:
    """Compara imágenes y calcula métricas de similitud."""

    def __init__(self) -> None:
        """Inicializa el ImageComparator."""
        pass

    def compare(
        self, image1_path: str, image2_path: str
    ) -> ComparisonResult:
        """Compara dos imágenes usando múltiples métricas.

        Args:
            image1_path: Ruta a la primera imagen.
            image2_path: Ruta a la segunda imagen.

        Returns:
            ComparisonResult con el resultado de la comparación.
        """
        logger.info(f"Comparando: {image1_path} vs {image2_path}")

        # Cargar imágenes
        img1 = self._load_image(image1_path)
        img2 = self._load_image(image2_path)

        # Redimensionar al mismo tamaño
        img1, img2 = self._resize_to_match(img1, img2)

        # Calcular SSIM
        ssim = self._calculate_ssim(img1, img2)

        # Calcular similitud de píxeles
        pixel_similarity = self._calculate_pixel_similarity(img1, img2)

        # Identificar diferencias
        differences = self._find_differences(img1, img2)

        # Calcular puntuación de calidad
        quality_score = self._calculate_quality_score(ssim, pixel_similarity)

        return ComparisonResult(
            ssim=ssim,
            clip_similarity=pixel_similarity,  # Usamos pixel similarity como proxy
            quality_score=quality_score,
            differences=differences,
            metadata={
                "image1_path": str(Path(image1_path)),
                "image2_path": str(Path(image2_path)),
            },
        )

    def render_svg(
        self,
        svg_code: str,
        output_path: str,
        width: int = 1024,
        height: int = 1024,
    ) -> None:
        """Renderiza un SVG a PNG.

        Args:
            svg_code: Código SVG a renderizar.
            output_path: Ruta donde guardar el PNG.
            width: Ancho de la imagen.
            height: Alto de la imagen.
        """
        import cairosvg

        logger.info(f"Renderizando SVG a: {output_path}")

        # Crear directorio si no existe
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Renderizar SVG
        try:
            cairosvg.svg2png(
                bytestring=svg_code.encode("utf-8"),
                write_to=output_path,
                output_width=width,
                output_height=height,
            )
        except Exception as e:
            logger.error(f"Error al renderizar SVG: {e}")
            raise

    def _load_image(self, image_path: str) -> np.ndarray:
        """Carga una imagen y la convierte a numpy array.

        Args:
            image_path: Ruta a la imagen.

        Returns:
            Array numpy con la imagen.
        """
        img = Image.open(image_path).convert("RGB")
        return np.array(img)

    def _resize_to_match(
        self, img1: np.ndarray, img2: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Redimensiona dos imágenes al mismo tamaño.

        Args:
            img1: Primera imagen.
            img2: Segunda imagen.

        Returns:
            Tupla con las imágenes redimensionadas.
        """
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]

        # Usar el tamaño más pequeño
        target_h = min(h1, h2)
        target_w = min(w1, w2)

        if h1 != target_h or w1 != target_w:
            img1 = self._resize_image(img1, target_w, target_h)

        if h2 != target_h or w2 != target_w:
            img2 = self._resize_image(img2, target_w, target_h)

        return img1, img2

    def _resize_image(
        self, img: np.ndarray, width: int, height: int
    ) -> np.ndarray:
        """Redimensiona una imagen.

        Args:
            img: Imagen a redimensionar.
            width: Ancho deseado.
            height: Alto deseado.

        Returns:
            Imagen redimensionada.
        """
        pil_img = Image.fromarray(img)
        resized = pil_img.resize((width, height), Image.LANCZOS)
        return np.array(resized)

    def _calculate_ssim(
        self, img1: np.ndarray, img2: np.ndarray
    ) -> float:
        """Calcula el índice de similitud estructural (SSIM).

        Args:
            img1: Primera imagen.
            img2: Segunda imagen.

        Returns:
            Valor SSIM entre 0 y 1.
        """
        from skimage.metrics import structural_similarity as ssim_func

        # Convertir a escala de grises
        gray1 = np.dot(img1[..., :3], [0.2989, 0.5870, 0.1140])
        gray2 = np.dot(img2[..., :3], [0.2989, 0.5870, 0.1140])

        # Calcular SSIM
        score = ssim_func(
            gray1, gray2, data_range=gray2.max() - gray2.min()
        )

        return float(score)

    def _calculate_pixel_similarity(
        self, img1: np.ndarray, img2: np.ndarray
    ) -> float:
        """Calcula la similitud de píxeles entre dos imágenes.

        Args:
            img1: Primera imagen.
            img2: Segunda imagen.

        Returns:
            Valor de similitud entre 0 y 1.
        """
        # Convertir a float y normalizar
        img1_float = img1.astype(np.float32) / 255.0
        img2_float = img2.astype(np.float32) / 255.0

        # Calcular diferencia absoluta
        diff = np.abs(img1_float - img2_float)

        # Calcular similitud (1 - media de diferencias)
        similarity = 1.0 - np.mean(diff)

        return float(similarity)

    def _find_differences(
        self, img1: np.ndarray, img2: np.ndarray
    ) -> List[dict]:
        """Identifica las diferencias entre dos imágenes.

        Args:
            img1: Primera imagen.
            img2: Segunda imagen.

        Returns:
            Lista de diferencias encontradas.
        """
        differences: List[dict] = []

        # Calcular diferencia absoluta
        diff = np.abs(img1.astype(np.int16) - img2.astype(np.int16))

        # Calcular umbral de diferencia
        threshold = 30  # Diferencia perceptible

        # Crear máscara de diferencias
        mask = np.any(diff > threshold, axis=2)

        # Si no hay diferencias significativas
        if not np.any(mask):
            return differences

        # Encontrar regiones con diferencias
        h, w = mask.shape

        # Dividir en cuadrantes para identificar áreas
        quadrants = [
            ("top_left", 0, 0, w // 2, h // 2),
            ("top_right", w // 2, 0, w, h // 2),
            ("bottom_left", 0, h // 2, w // 2, h),
            ("bottom_right", w // 2, h // 2, w, h),
            ("center", w // 4, h // 4, 3 * w // 4, 3 * h // 4),
        ]

        for name, x1, y1, x2, y2 in quadrants:
            quadrant_mask = mask[y1:y2, x1:x2]
            diff_pixels = np.sum(quadrant_mask)
            total_pixels = (y2 - y1) * (x2 - x1)
            diff_ratio = diff_pixels / total_pixels if total_pixels > 0 else 0

            if diff_ratio > 0.01:  # Más del 1% de diferencia
                # Determinar tipo de diferencia predominante
                quadrant_diff = diff[y1:y2, x1:x2]
                avg_diff = np.mean(quadrant_diff)

                if avg_diff < 50:
                    issue = "color_mismatch"
                elif avg_diff < 100:
                    issue = "shape_precision"
                else:
                    issue = "missing_details"

                differences.append(
                    {
                        "area": name,
                        "issue": issue,
                        "diff_ratio": float(diff_ratio),
                        "severity": "high" if diff_ratio > 0.1 else "medium",
                    }
                )

        return differences

    def _calculate_quality_score(
        self, ssim: float, pixel_similarity: float
    ) -> float:
        """Calcula una puntuación de calidad global.

        Args:
            ssim: Valor SSIM.
            pixel_similarity: Valor de similitud de píxeles.

        Returns:
            Puntuación de calidad entre 0 y 1.
        """
        # Ponderar SSIM y similitud de píxeles
        # SSIM es más importante para similitud estructural
        weight_ssim = 0.6
        weight_pixel = 0.4

        quality = (ssim * weight_ssim) + (pixel_similarity * weight_pixel)

        return min(max(quality, 0.0), 1.0)
