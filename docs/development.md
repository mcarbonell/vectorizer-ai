# Guía de Desarrollo

## Configuración del Entorno de Desarrollo

### Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- git
- Editor de código (VS Code recomendado)
- GTK3 Runtime (Windows, requerido para renderizado SVG)
  - Instalar: `winget install --id=tschoonj.GTKForWindows -e`

### Configuración Inicial

```bash
# Clonar el repositorio
git clone https://github.com/mcarbonell/vectorizer-ai.git
cd vectorizer-ai

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Instalar pre-commit hooks
pre-commit install
```

### Estructura del Proyecto

```
vectorizer-ai/
├── src/
│   └── vectorizer/
│       ├── __init__.py
│       ├── core.py              # Lógica principal
│       ├── vision.py            # Integración con APIs de visión
│       ├── svg_generator.py     # Generación de SVG
│       ├── comparator.py        # Comparación de imágenes
│       └── metrics.py           # Métricas de calidad
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_vision.py
│   ├── test_svg_generator.py
│   └── test_metrics.py
├── docs/                        # Documentación
├── examples/                    # Ejemplos de uso
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore
├── pyproject.toml               # Configuración del proyecto
├── requirements.txt             # Dependencias de producción
└── requirements-dev.txt         # Dependencias de desarrollo
```

## Flujo de Trabajo de Desarrollo

### 1. Crear una Rama Nueva

```bash
# Actualizar main
git checkout main
git pull origin main

# Crear rama de feature
git checkout -b feature/nombre-de-la-funcionalidad

# O para bugfix
git checkout -b fix/descripcion-del-bug
```

### 2. Escribir Código

```bash
# Crear archivos necesarios
# Editar código existente
# Asegurarse de seguir las convenciones del proyecto
```

### 3. Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con cobertura
pytest --cov=src/vectorizer

# Ejecutar tests específicos
pytest tests/test_vision.py

# Ejecutar tests en modo verbose
pytest -v
```

### 4. Formatear y Lintear

```bash
# Formatear código con black
black src/ tests/

# Lintear con flake8
flake8 src/ tests/

# Verificar tipos con mypy
mypy src/

# Ejecutar pre-commit en todos los archivos
pre-commit run --all-files
```

### 5. Commit y Push

```bash
# Añadir archivos
git add .

# Crear commit con mensaje descriptivo
git commit -m "feat: agregar funcionalidad X"

# Push a la rama
git push origin feature/nombre-de-la-funcionalidad
```

### 6. Crear Pull Request

1. Ir a GitHub/GitLab
2. Crear Pull Request desde tu rama
3. Completar la plantilla de PR
4. Solicitar revisión
5. Address feedback
6. Merge cuando sea aprobado

## Convenciones de Código

### Estilo de Código

- Seguir PEP 8
- Usar Black para formateo
- Máximo 88 caracteres por línea
- Imports ordenados (stdlib, third-party, local)

### Nombres

- **Variables y funciones**: `snake_case`
- **Clases**: `PascalCase`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Módulos privados**: `_leading_underscore`

### Docstrings

Usar Google Style Docstrings:

```python
def analyze_image(image_path: str) -> dict:
    """Analiza una imagen y extrae características visuales.

    Args:
        image_path: Ruta al archivo de imagen a analizar.

    Returns:
        Diccionario con características extraídas incluyendo formas,
        colores y composición.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el formato de imagen no es soportado.
    """
    pass
```

### Type Hints

Siempre incluir type hints:

```python
from typing import List, Dict, Optional

def process_svg(svg_code: str, optimize: bool = True) -> str:
    """Procesa y opcionalmente optimiza código SVG."""
    pass
```

## Testing

### Escribir Tests

Usar pytest:

```python
import pytest
from vectorizer.vision import VisionAnalyzer

def test_vision_analyzer_initialization():
    """Prueba la inicialización del VisionAnalyzer."""
    analyzer = VisionAnalyzer(api_key="test-key")
    assert analyzer is not None
    assert analyzer.api_key == "test-key"

@pytest.mark.asyncio
async def test_analyze_image():
    """Prueba el análisis de una imagen."""
    analyzer = VisionAnalyzer(api_key="test-key")
    result = await analyzer.analyze("test_image.png")
    assert "shapes" in result
    assert "colors" in result
```

### Fixtures

Usar fixtures para configuración común:

```python
@pytest.fixture
def sample_image():
    """Proporciona una imagen de prueba."""
    return "tests/fixtures/sample.png"

@pytest.fixture
def vision_analyzer():
    """Proporciona una instancia de VisionAnalyzer."""
    return VisionAnalyzer(api_key="test-key")
```

### Mocking

Usar unittest.mock para APIs externas:

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_analyze_with_mock():
    """Prueba el análisis con API mockeada."""
    analyzer = VisionAnalyzer(api_key="test-key")
    
    with patch.object(analyzer, '_call_api', new_callable=AsyncMock) as mock_api:
        mock_api.return_value = {"shapes": ["circle"], "colors": ["#FF0000"]}
        result = await analyzer.analyze("test.png")
        
        mock_api.assert_called_once()
        assert result["shapes"] == ["circle"]
```

## Debugging

### Logging

Configurar logging apropiadamente:

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.debug("Iniciando función")
    logger.info("Procesando datos")
    logger.warning("Advertencia: valor inesperado")
    logger.error("Error crítico")
```

### Debugging con pdb

```python
import pdb

def some_function():
    # Punto de interrupción
    pdb.set_trace()
    # Código a debuggear
    pass
```

### VS Code Debugging

Crear `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {
                "ANTHROPIC_API_KEY": "your-key-here"
            }
        }
    ]
}
```

## Manejo de APIs Externas

### Rate Limiting

Implementar rate limiting:

```python
import time
from functools import wraps

def rate_limit(max_calls: int, time_window: int):
    """Decorador para limitar llamadas a API."""
    calls = []
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()
            # Remover llamadas antiguas
            calls[:] = [c for c in calls if c > now - time_window]
            
            if len(calls) >= max_calls:
                sleep_time = time_window - (now - calls[0])
                await asyncio.sleep(sleep_time)
                calls.pop(0)
            
            calls.append(now)
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### Retry Logic

Implementar reintentos con backoff:

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_api_with_retry():
    """Llama a la API con reintentos."""
    # Llamada a API
    pass
```

## Performance

### Profiling

Usar cProfile:

```python
import cProfile
import pstats

def profile_function():
    """Profilea una función."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Código a profilear
    result = some_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result
```

### Optimización

- Usar async/await para I/O
- Cachear resultados cuando sea posible
- Evitar cálculos redundantes
- Usar estructuras de datos apropiadas

## Documentación

### Actualizar README

Mantener el README actualizado con:
- Nuevas características
- Cambios en la API
- Ejemplos de uso
- Instrucciones de instalación

### Actualizar CHANGELOG

Mantener un CHANGELOG.md:

```markdown
# Changelog

## [Unreleased]

### Added
- Nueva funcionalidad X

### Changed
- Cambio en comportamiento Y

### Fixed
- Bug fix Z

## [1.0.0] - 2024-01-01

### Added
- Versión inicial
```

### Code Comments

Comentar código complejo:

```python
# Este algoritmo implementa el método de optimización X
# Referencia: https://example.com/paper
def optimize_svg(svg_code: str) -> str:
    # Paso 1: Analizar estructura del SVG
    # ...
    pass
```

## Release Process

### Preparar Release

```bash
# Actualizar versión en pyproject.toml
# Actualizar CHANGELOG
# Crear tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Publicar a PyPI

```bash
# Construir paquete
python -m build

# Publicar a PyPI (test primero)
twine upload --repository testpypi dist/*

# Publicar a PyPI (producción)
twine upload dist/*
```

## Recursos Útiles

- [Python Documentation](https://docs.python.org/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [mypy Type Checker](https://mypy.readthedocs.io/)
