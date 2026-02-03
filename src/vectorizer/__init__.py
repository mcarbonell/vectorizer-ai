"""Vectorizer AI - Vectorizador de imágenes impulsado por IA."""

from .core import Vectorizer
from .vision import VisionAnalyzer
from .svg_generator import SVGGenerator
from .comparator import ImageComparator
from .metrics import MetricsEngine

__all__ = [
    "Vectorizer",
    "VisionAnalyzer",
    "SVGGenerator",
    "ImageComparator",
    "MetricsEngine",
]

__version__ = "0.1.0"
