"""Modelos de datos para Vectorizer AI."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ImageAnalysis:
    """Resultado del análisis de una imagen."""

    shapes: List[str]
    colors: List[str]
    composition: str
    complexity: str
    style: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SVGGeneration:
    """Resultado de la generación de SVG."""

    svg_code: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    iteration: int = 0


@dataclass
class ComparisonResult:
    """Resultado de la comparación de imágenes."""

    ssim: float
    clip_similarity: float
    quality_score: float
    differences: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorizationResult:
    """Resultado del proceso de vectorización."""

    svg_code: str
    quality: float
    iterations: int
    metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchResult:
    """Resultado del procesamiento batch de múltiples imágenes."""

    total: int
    successful: int
    failed: int
    results: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
