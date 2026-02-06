from __future__ import annotations

"""Módulo de métricas de calidad para Vectorizer AI."""

import logging
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

from .models import ComparisonResult

if TYPE_CHECKING:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torchvision import transforms

logger = logging.getLogger(__name__)

try:
    import torch  # noqa: F811
    import torch.nn as nn  # noqa: F811
    import torch.nn.functional as F  # noqa: F811
    from torchvision import transforms  # noqa: F811

    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


class MetricsEngine:
    """Calcula métricas de calidad entre imágenes."""

    def __init__(
        self,
        enable_clip: bool = True,
        enable_ssim: bool = True,
        enable_lpips: bool = False,
    ) -> None:
        """Inicializa el MetricsEngine.

        Args:
            enable_clip: Habilitar métricas CLIP.
            enable_ssim: Habilitar métricas SSIM.
            enable_lpips: Habilitar métricas LPIPS.
        """
        self.enable_clip = enable_clip
        self.enable_ssim = enable_ssim
        self.enable_lpips = enable_lpips

    def calculate_ssim(self, image1_path: str, image2_path: str) -> float:
        """Calcula el índice de similitud estructural (SSIM).

        Args:
            image1_path: Ruta a la primera imagen.
            image2_path: Ruta a la segunda imagen.

        Returns:
            Valor SSIM entre 0 y 1.
        """
        logger.info(f"Calculando SSIM: {image1_path} vs {image2_path}")

        # Cargar imágenes
        img1 = self._load_image(image1_path)
        img2 = self._load_image(image2_path)

        # Redimensionar al mismo tamaño
        img1, img2 = self._resize_to_match(img1, img2)

        # Calcular SSIM
        return self._calculate_ssim(img1, img2)

    def calculate_clip_similarity(self, image1_path: str, image2_path: str) -> float:
        """Calcula la similitud usando CLIP embeddings.

        Args:
            image1_path: Ruta a la primera imagen.
            image2_path: Ruta a la segunda imagen.

        Returns:
            Valor de similitud entre 0 y 1.
        """
        logger.info(f"Calculando similitud CLIP: {image1_path} vs {image2_path}")

        # TODO: Implementar con CLIP
        # Por ahora retornar un valor basado en similitud de píxeles
        logger.warning("CLIP similarity no implementado, usando pixel similarity")

        # Cargar y procesar imágenes
        img1 = self._load_image(image1_path)
        img2 = self._load_image(image2_path)

        img1, img2 = self._resize_to_match(img1, img2)

        return self._calculate_pixel_similarity(img1, img2)

    def calculate_lpips(self, image1_path: str, image2_path: str) -> float:
        """Calcula LPIPS (Learned Perceptual Image Patch Similarity).

        Args:
            image1_path: Ruta a la primera imagen.
            image2_path: Ruta a la segunda imagen.

        Returns:
            Valor LPIPS entre 0 y 1 (invertido para mayor similitud).
        """
        logger.info(f"Calculando LPIPS: {image1_path} vs {image2_path}")

        if not HAS_TORCH:
            logger.warning(
                "PyTorch no disponible. Instala con: pip install vectorizer-ai[ml]"
            )
            img1 = self._load_image(image1_path)
            img2 = self._load_image(image2_path)
            img1, img2 = self._resize_to_match(img1, img2)
            return self._calculate_pixel_similarity(img1, img2)

        try:
            # Cargar imágenes
            img1 = self._load_image(image1_path)
            img2 = self._load_image(image2_path)

            # Redimensionar a 256x256 para LPIPS
            img1 = self._resize_image(img1, 256, 256)
            img2 = self._resize_image(img2, 256, 256)

            # Normalizar para torchvision
            normalize = transforms.Normalize(
                mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            )

            # Convertir a tensores
            tensor1 = torch.from_numpy(img1).permute(2, 0, 1).float() / 255.0
            tensor2 = torch.from_numpy(img2).permute(2, 0, 1).float() / 255.0

            tensor1 = normalize(tensor1).unsqueeze(0)
            tensor2 = normalize(tensor2).unsqueeze(0)

            # Usar una red simple para calcular características
            # (En producción usaríamos una red VGG pre-entrenada)
            features1 = self._extract_features(tensor1)
            features2 = self._extract_features(tensor2)

            # Calcular distancia L2
            lpips_distance = F.mse_loss(features1, features2).item()

            # Invertir para obtener similitud (0-1)
            similarity = 1.0 / (1.0 + lpips_distance * 100)

            return similarity

        except Exception as e:
            logger.error(f"Error calculando LPIPS: {e}")
            return self._calculate_pixel_similarity(img1, img2)

    def calculate_quality_score(self, comparison_result: ComparisonResult) -> float:
        """Calcula una puntuación de calidad global.

        Args:
            comparison_result: Resultado de la comparación.

        Returns:
            Puntuación de calidad entre 0 y 1.
        """
        ssim = comparison_result.ssim
        clip_similarity = comparison_result.clip_similarity

        quality = self._calculate_quality_score(ssim, clip_similarity)

        logger.info(f"Quality score: {quality:.4f}")

        return quality

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
    ) -> tuple[np.ndarray, np.ndarray]:
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

    def _resize_image(self, img: np.ndarray, width: int, height: int) -> np.ndarray:
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

    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
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

        # Calcular SSIM con data_range correcto (255 para imágenes de 8 bits)
        score = ssim_func(gray1, gray2, data_range=255.0)

        # Asegurar que el resultado está entre 0 y 1
        score = max(0.0, min(1.0, float(score)))

        return score

    def _calculate_pixel_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calcula la similitud de píxeles.

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

    def _extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extrae características usando una red simple.

        Args:
            x: Tensor de imagen.

        Returns:
            Tensor de características.
        """
        if not HAS_TORCH:
            raise RuntimeError("PyTorch no disponible")

        # Red convolucional simple para extraer características
        features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )

        with torch.no_grad():
            out = features(x)
            out = out.view(out.size(0), -1)

        return out

    def _calculate_quality_score(self, ssim: float, clip_similarity: float) -> float:
        """Calcula una puntuación de calidad global.

        Args:
            ssim: Valor SSIM.
            clip_similarity: Valor de similitud CLIP.

        Returns:
            Puntuación de calidad entre 0 y 1.
        """
        # Ponderar SSIM y CLIP
        # SSIM es más importante para similitud estructural
        # CLIP es más importante para similitud semántica
        weight_ssim = 0.6
        weight_clip = 0.4

        quality = (ssim * weight_ssim) + (clip_similarity * weight_clip)

        return min(max(quality, 0.0), 1.0)
