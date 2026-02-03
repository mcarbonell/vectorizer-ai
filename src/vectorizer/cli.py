"""Interfaz de línea de comandos para Vectorizer AI."""

import logging
import os
from pathlib import Path

import click
from dotenv import load_dotenv

from .core import Vectorizer

# Cargar variables de entorno desde .env
load_dotenv()

logger = logging.getLogger(__name__)


@click.command()
@click.argument("input", type=click.Path(exists=True))
@click.argument("output")
@click.option(
    "--model",
    "-m",
    default="claude-3-5-sonnet-20241022",
    help="Modelo de IA a usar",
)
@click.option(
    "--max-iterations",
    "-i",
    default=10,
    help="Numero maximo de iteraciones",
)
@click.option(
    "--quality-threshold",
    "-q",
    default=0.85,
    help="Umbral de calidad",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Mostrar informacion detallada",
)
@click.option(
    "--temp-dir",
    "-t",
    default="./temp",
    help="Directorio temporal",
)
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["anthropic", "openai", "openrouter", "google"]),
    default="anthropic",
    help="Proveedor de API",
)
@click.option(
    "--api-key",
    "-k",
    default=None,
    help="API key (o usar variable de entorno)",
)
@click.option(
    "--base-url",
    "-b",
    default=None,
    help="URL base personalizada (para OpenRouter, LM Studio, etc.)",
)
@click.option(
    "--estimate-cost",
    is_flag=True,
    help="Mostrar estimación de costo sin ejecutar",
)
def main(
    input: str,
    output: str,
    model: str,
    max_iterations: int,
    quality_threshold: float,
    verbose: bool,
    temp_dir: str,
    provider: str,
    api_key: str,
    base_url: str,
    estimate_cost: bool,
) -> None:
    """Vectoriza una imagen a SVG usando IA."""
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    # Get API key from parameter or environment
    if api_key:
        pass  # Use provided key
    elif provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    elif provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
    elif provider == "openrouter":
        api_key = os.environ.get("OPENROUTER_API_KEY")
    elif provider == "google":
        api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        click.echo(
            f"Error: API key no encontrada para {provider}. "
            f"Usa --api-key o configura la variable de entorno correspondiente.",
            err=True
        )
        raise click.Abort()
    
    # Validar parámetros
    if max_iterations < 1 or max_iterations > 100:
        click.echo("Error: max-iterations debe estar entre 1 y 100", err=True)
        raise click.Abort()
    
    if not 0.0 <= quality_threshold <= 1.0:
        click.echo("Error: quality-threshold debe estar entre 0.0 y 1.0", err=True)
        raise click.Abort()

    click.echo(f"Proveedor: {provider}")
    click.echo(f"Modelo: {model}")
    click.echo(f"Max iteraciones: {max_iterations}")
    click.echo(f"Calidad threshold: {quality_threshold}")
    click.echo(f"Input: {input}")
    click.echo(f"Output: {output}")
    click.echo(f"Temp dir: {temp_dir}")
    click.echo(f"Verbose: {verbose}")

    if base_url:
        click.echo(f"Base URL: {base_url}")
    
    # Estimación de costo
    if estimate_cost:
        from pathlib import Path
        from vectorizer.cost_estimator import CostEstimator
        
        input_file = Path(input)
        if input_file.exists():
            size_kb = input_file.stat().st_size / 1024
        else:
            size_kb = 100  # Default
        
        estimator = CostEstimator(provider=provider, model=model)
        estimate_str = estimator.format_estimate(size_kb, max_iterations)
        
        click.echo("")
        click.echo("=" * 50)
        click.echo(estimate_str)
        click.echo("=" * 50)
        return

    try:
        # Initialize vectorizer
        vectorizer = Vectorizer(
            api_key=api_key,
            model=model,
            max_iterations=max_iterations,
            quality_threshold=quality_threshold,
            temp_dir=temp_dir,
            verbose=verbose,
            provider=provider,
            base_url=base_url if base_url else None,
        )

        # Progress callback
        def progress_callback(iteration: int, quality: float) -> None:
            click.echo(f"Iteracion {iteration}/{max_iterations} - Calidad: {quality:.4f}")

        # Run vectorization
        result = vectorizer.vectorize(input, output, callback=progress_callback)

        # Show results
        click.echo("")
        click.echo("=" * 50)
        click.echo("Vectorizacion completada!")
        click.echo(f"Iteraciones: {result.iterations}")
        click.echo(f"Calidad final: {result.quality:.4f}")
        if "ssim" in result.metrics:
            click.echo(f"SSIM: {result.metrics['ssim']:.4f}")
        if "clip_similarity" in result.metrics:
            click.echo(f"CLIP: {result.metrics['clip_similarity']:.4f}")
        click.echo(f"SVG guardado en: {output}")
        click.echo("=" * 50)

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except RuntimeError as e:
        click.echo(f"Error crítico: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error inesperado: {e}", err=True)
        if verbose:
            raise
        raise click.Abort()


if __name__ == "__main__":
    main()
