"""Vectorizer AI - Vectorizador de imágenes impulsado por IA."""

from .cache import CacheManager
from .comparator import ImageComparator
from .core import Vectorizer
from .cost_estimator import CostEstimator
from .metrics import MetricsEngine
from .models import BatchResult, VectorizationResult
from .svg_generator import SVGGenerator
from .vision import VisionAnalyzer

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
