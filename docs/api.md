# API Reference

## Módulo Principal: `vectorizer`

### `Vectorizer`

Clase principal que orquesta el proceso de vectorización.

```python
from vectorizer import Vectorizer

vectorizer = Vectorizer(
    api_key="your-api-key",
    model="claude-3-5-sonnet-20241022",
    max_iterations=10,
    quality_threshold=0.85
)

result = vectorizer.vectorize(
    input_path="input.png",
    output_path="output.svg"
)
```

#### Constructor

```python
def __init__(
    api_key: str,
    model: str = "claude-3-5-sonnet-20241022",
    max_iterations: int = 10,
    quality_threshold: float = 0.85,
    temp_dir: str = "./temp",
    verbose: bool = False
) -> None
```

**Parámetros:**
- `api_key` (str): API key para el servicio de IA
- `model` (str): Modelo de IA a usar (default: "claude-3-5-sonnet-20241022")
- `max_iterations` (int): Número máximo de iteraciones (default: 10)
- `quality_threshold` (float): Umbral de calidad para detener (default: 0.85)
- `temp_dir` (str): Directorio para archivos temporales (default: "./temp")
- `verbose` (bool): Mostrar información detallada (default: False)

#### Métodos

##### `vectorize()`

```python
def vectorize(
    input_path: str,
    output_path: str,
    callback: Optional[Callable[[int, float], None]] = None
) -> VectorizationResult
```

Vectoriza una imagen y guarda el resultado.

**Parámetros:**
- `input_path` (str): Ruta a la imagen de entrada
- `output_path` (str): Ruta donde guardar el SVG resultante
- `callback` (Optional[Callable]): Función llamada en cada iteración con (iteración, calidad)

**Retorna:**
- `VectorizationResult`: Objeto con el resultado de la vectorización

**Lanza:**
- `FileNotFoundError`: Si el archivo de entrada no existe
- `ValueError`: Si el formato de imagen no es soportado
- `APIError`: Si hay un error en la llamada a la API

##### `vectorize_async()`

```python
async def vectorize_async(
    input_path: str,
    output_path: str,
    callback: Optional[Callable[[int, float], None]] = None
) -> VectorizationResult
```

Versión asíncrona de `vectorize()`.

## Módulo: `vectorizer.vision`

### `VisionAnalyzer`

Analiza imágenes usando APIs de visión.

```python
from vectorizer.vision import VisionAnalyzer

analyzer = VisionAnalyzer(api_key="your-api-key")
analysis = await analyzer.analyze("image.png")
```

#### Constructor

```python
def __init__(
    api_key: str,
    model: str = "claude-3-5-sonnet-20241022",
    provider: str = "anthropic"
) -> None
```

**Parámetros:**
- `api_key` (str): API key para el servicio de IA
- `model` (str): Modelo de IA a usar
- `provider` (str): Proveedor de API ("anthropic" o "openai")

#### Métodos

##### `analyze()`

```python
async def analyze(
    image_path: str,
    detail_level: str = "medium"
) -> ImageAnalysis
```

Analiza una imagen y extrae características visuales.

**Parámetros:**
- `image_path` (str): Ruta a la imagen a analizar
- `detail_level` (str): Nivel de detalle ("low", "medium", "high")

**Retorna:**
- `ImageAnalysis`: Objeto con el análisis de la imagen

##### `compare()`

```python
async def compare(
    image1_path: str,
    image2_path: str
) -> ComparisonResult
```

Compara dos imágenes y devuelve las diferencias.

**Parámetros:**
- `image1_path` (str): Ruta a la primera imagen
- `image2_path` (str): Ruta a la segunda imagen

**Retorna:**
- `ComparisonResult`: Objeto con el resultado de la comparación

## Módulo: `vectorizer.svg_generator`

### `SVGGenerator`

Genera y modifica código SVG.

```python
from vectorizer.svg_generator import SVGGenerator

generator = SVGGenerator(api_key="your-api-key")
svg = await generator.generate(analysis)
```

#### Constructor

```python
def __init__(
    api_key: str,
    model: str = "claude-3-5-sonnet-20241022"
) -> None
```

#### Métodos

##### `generate()`

```python
async def generate(
    analysis: ImageAnalysis,
    style: str = "flat"
) -> SVGGeneration
```

Genera un SVG basado en el análisis de una imagen.

**Parámetros:**
- `analysis` (ImageAnalysis): Análisis de la imagen
- `style` (str): Estilo del SVG ("flat", "outline", "detailed")

**Retorna:**
- `SVGGeneration`: Objeto con el SVG generado

##### `modify()`

```python
async def modify(
    svg_code: str,
    modifications: List[str]
) -> SVGGeneration
```

Modifica un SVG existente según las instrucciones.

**Parámetros:**
- `svg_code` (str): Código SVG a modificar
- `modifications` (List[str]): Lista de modificaciones a aplicar

**Retorna:**
- `SVGGeneration`: Objeto con el SVG modificado

##### `optimize()`

```python
def optimize(
    svg_code: str,
    level: str = "medium"
) -> str
```

Optimiza el código SVG reduciendo su tamaño.

**Parámetros:**
- `svg_code` (str): Código SVG a optimizar
- `level` (str): Nivel de optimización ("low", "medium", "high")

**Retorna:**
- `str`: Código SVG optimizado

## Módulo: `vectorizer.comparator`

### `ImageComparator`

Compara imágenes y calcula métricas de similitud.

```python
from vectorizer.comparator import ImageComparator

comparator = ImageComparator()
result = comparator.compare("image1.png", "image2.png")
```

#### Métodos

##### `compare()`

```python
def compare(
    image1_path: str,
    image2_path: str
) -> ComparisonResult
```

Compara dos imágenes usando múltiples métricas.

**Parámetros:**
- `image1_path` (str): Ruta a la primera imagen
- `image2_path` (str): Ruta a la segunda imagen

**Retorna:**
- `ComparisonResult`: Objeto con el resultado de la comparación

##### `render_svg()`

```python
def render_svg(
    svg_code: str,
    output_path: str,
    width: int = 1024,
    height: int = 1024
) -> None
```

Renderiza un SVG a PNG.

**Parámetros:**
- `svg_code` (str): Código SVG a renderizar
- `output_path` (str): Ruta donde guardar el PNG
- `width` (int): Ancho de la imagen (default: 1024)
- `height` (int): Alto de la imagen (default: 1024)

## Módulo: `vectorizer.metrics`

### `MetricsEngine`

Calcula métricas de calidad entre imágenes.

```python
from vectorizer.metrics import MetricsEngine

engine = MetricsEngine()
ssim = engine.calculate_ssim("image1.png", "image2.png")
```

#### Métodos

##### `calculate_ssim()`

```python
def calculate_ssim(
    image1_path: str,
    image2_path: str
) -> float
```

Calcula el índice de similitud estructural (SSIM).

**Parámetros:**
- `image1_path` (str): Ruta a la primera imagen
- `image2_path` (str): Ruta a la segunda imagen

**Retorna:**
- `float`: Valor SSIM entre 0 y 1

##### `calculate_clip_similarity()`

```python
def calculate_clip_similarity(
    image1_path: str,
    image2_path: str
) -> float
```

Calcula la similitud usando CLIP embeddings.

**Parámetros:**
- `image1_path` (str): Ruta a la primera imagen
- `image2_path` (str): Ruta a la segunda imagen

**Retorna:**
- `float`: Valor de similitud entre 0 y 1

##### `calculate_quality_score()`

```python
def calculate_quality_score(
    comparison_result: ComparisonResult
) -> float
```

Calcula una puntuación de calidad global.

**Parámetros:**
- `comparison_result` (ComparisonResult): Resultado de la comparación

**Retorna:**
- `float`: Puntuación de calidad entre 0 y 1

## Modelos de Datos

### `ImageAnalysis`

```python
@dataclass
class ImageAnalysis:
    shapes: List[str]
    colors: List[str]
    composition: str
    complexity: str
    style: str
    description: str
    metadata: Dict[str, Any]
```

### `SVGGeneration`

```python
@dataclass
class SVGGeneration:
    svg_code: str
    metadata: Dict[str, Any]
    iteration: int = 0
```

### `ComparisonResult`

```python
@dataclass
class ComparisonResult:
    ssim: float
    clip_similarity: float
    quality_score: float
    differences: List[Dict[str, Any]]
    metadata: Dict[str, Any]
```

### `VectorizationResult`

```python
@dataclass
class VectorizationResult:
    svg_code: str
    quality: float
    iterations: int
    metrics: Dict[str, float]
    metadata: Dict[str, Any]
```

## Excepciones

### `VectorizerError`

Excepción base para todos los errores del vectorizador.

```python
class VectorizerError(Exception):
    """Excepción base para errores de vectorización."""
    pass
```

### `APIError`

Error en la llamada a la API de IA.

```python
class APIError(VectorizerError):
    """Error en la llamada a la API."""
    pass
```

### `ImageProcessingError`

Error en el procesamiento de imágenes.

```python
class ImageProcessingError(VectorizerError):
    """Error en el procesamiento de imágenes."""
    pass
```

### `SVGGenerationError`

Error en la generación de SVG.

```python
class SVGGenerationError(VectorizerError):
    """Error en la generación de SVG."""
    pass
```

## CLI

### Comando: `vectorizer`

```bash
python -m vectorizer INPUT OUTPUT [OPTIONS]
```

#### Argumentos

- `INPUT`: Ruta a la imagen de entrada
- `OUTPUT`: Ruta donde guardar el SVG resultante

#### Opciones

- `--model, -m`: Modelo de IA a usar (default: claude-3-5-sonnet-20241022)
- `--max-iterations, -i`: Número máximo de iteraciones (default: 10)
- `--quality-threshold, -q`: Umbral de calidad (default: 0.85)
- `--verbose, -v`: Mostrar información detallada
- `--temp-dir, -t`: Directorio temporal (default: ./temp)
- `--help, -h`: Mostrar ayuda

#### Ejemplos

```bash
# Uso básico
python -m vectorizer input.png output.svg

# Con opciones personalizadas
python -m vectorizer input.png output.svg \
    --max-iterations 15 \
    --quality-threshold 0.9 \
    --verbose

# Usar modelo específico
python -m vectorizer input.png output.svg \
    --model gpt-4-vision-preview
```

## Configuración

### Variables de Entorno

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Configuración
MAX_ITERATIONS=10
QUALITY_THRESHOLD=0.85
DEFAULT_MODEL=claude-3-5-sonnet-20241022

# Rutas
TEMP_DIR=./temp
OUTPUT_DIR=./output
```

### Archivo de Configuración

Crear un archivo `.env` en la raíz del proyecto:

```env
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
MAX_ITERATIONS=10
QUALITY_THRESHOLD=0.85
DEFAULT_MODEL=claude-3-5-sonnet-20241022
TEMP_DIR=./temp
OUTPUT_DIR=./output
```
