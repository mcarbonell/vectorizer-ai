"""Vectorizer AI - Vectorizador de imágenes impulsado por IA."""

from .core import Vectorizer
from .vision import VisionAnalyzer
from .svg_generator import SVGGenerator
from .comparator import ImageComparator
from .metrics import MetricsEngine
from .cache import CacheManager
from .cost_estimator import CostEstimator
from .models import BatchResult, VectorizationResult

__all__ = [
    "Vectorizer",
    "VisionAnalyzer",
    "SVGGenerator",
    "ImageComparator",
    "MetricsEngine",
    "CacheManager",
    "CostEstimator",
    "BatchResult",
    "VectorizationResult",
]

__version__ = "0.2.0"
