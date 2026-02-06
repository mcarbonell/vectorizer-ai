"""Estimador de costos de API para Vectorizer AI."""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class CostEstimator:
    """Estima costos de uso de APIs."""

    # Costos por 1M tokens (aproximados, actualizar según pricing real)
    COSTS = {
        "anthropic": {
            "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
            "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
        },
        "openai": {
            "gpt-4-vision-preview": {"input": 10.0, "output": 30.0},
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        },
        "google": {
            "gemini-2.0-flash-exp": {"input": 0.0, "output": 0.0},  # Gratis
            "gemini-1.5-pro": {"input": 1.25, "output": 5.0},
        },
    }

    def __init__(self, provider: str, model: str):
        """Inicializa el estimador.

        Args:
            provider: Proveedor de API.
            model: Modelo a usar.
        """
        self.provider = provider
        self.model = model

    def estimate_tokens(
        self, image_size_kb: float, max_iterations: int
    ) -> Dict[str, int]:
        """Estima tokens necesarios.

        Args:
            image_size_kb: Tamaño de imagen en KB.
            max_iterations: Número máximo de iteraciones.

        Returns:
            Dict con tokens estimados (input, output).
        """
        # Estimación aproximada
        # Análisis inicial: ~1000 tokens input (imagen + prompt), ~500 output
        # Generación SVG: ~500 input, ~2000 output
        # Modificación por iteración: ~1000 input, ~2000 output

        input_tokens = 1000 + 500  # Análisis + generación inicial
        output_tokens = 500 + 2000

        # Por cada iteración adicional
        input_tokens += (max_iterations - 1) * 1000
        output_tokens += (max_iterations - 1) * 2000

        return {"input": input_tokens, "output": output_tokens}

    def estimate_cost(
        self, image_size_kb: float, max_iterations: int
    ) -> Dict[str, float]:
        """Estima costo total.

        Args:
            image_size_kb: Tamaño de imagen en KB.
            max_iterations: Número máximo de iteraciones.

        Returns:
            Dict con costos estimados.
        """
        tokens = self.estimate_tokens(image_size_kb, max_iterations)

        # Obtener costos del modelo
        if self.provider not in self.COSTS:
            logger.warning(f"Costos no disponibles para {self.provider}")
            return {"input": 0.0, "output": 0.0, "total": 0.0}

        model_costs = self.COSTS[self.provider].get(self.model)
        if not model_costs:
            # Usar primer modelo como default
            model_costs = list(self.COSTS[self.provider].values())[0]
            logger.warning(f"Usando costos default para {self.model}")

        # Calcular costos (por millón de tokens)
        input_cost = (tokens["input"] / 1_000_000) * model_costs["input"]
        output_cost = (tokens["output"] / 1_000_000) * model_costs["output"]
        total_cost = input_cost + output_cost

        return {
            "input": round(input_cost, 4),
            "output": round(output_cost, 4),
            "total": round(total_cost, 4),
            "tokens": tokens,
        }

    def format_estimate(self, image_size_kb: float, max_iterations: int) -> str:
        """Formatea estimación para mostrar.

        Args:
            image_size_kb: Tamaño de imagen en KB.
            max_iterations: Número máximo de iteraciones.

        Returns:
            String formateado con estimación.
        """
        estimate = self.estimate_cost(image_size_kb, max_iterations)

        if estimate["total"] == 0.0:
            return f"Costo estimado: GRATIS ({self.provider}/{self.model})"

        return (
            f"Costo estimado: ${estimate['total']:.4f}\n"
            f"  - Input: ${estimate['input']:.4f} "
            f"({estimate['tokens']['input']} tokens)\n"
            f"  - Output: ${estimate['output']:.4f} "
            f"({estimate['tokens']['output']} tokens)\n"
            f"  - Proveedor: {self.provider}/{self.model}"
        )
