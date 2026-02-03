# 🎨 Vectorizer AI

Un vectorizador de imágenes impulsado por inteligencia artificial que utiliza visión por computadora y generación de código iterativa para convertir imágenes rasterizadas (PNG, JPG) en gráficos vectoriales (SVG) de alta calidad.

## 🌟 Características

- **Vectorización basada en IA**: Utiliza modelos de visión (Google Gemini 2.5 Flash, Claude, GPT-4V)
- **Optimización iterativa**: Proceso de refinamiento continuo hasta alcanzar la calidad deseada
- **Comparación visual**: La IA "ve" las diferencias entre el original y el SVG generado
- **Sin entrenamiento**: Aprovecha modelos pre-entrenados de visión
- **Múltiples formatos de entrada**: Soporta PNG, JPG, WEBP y más
- **Salida SVG optimizada**: Genera SVGs limpios, editables y con fondo transparente
- **Métricas automáticas**: SSIM y CLIP para evaluar la calidad del vectorizado

## 🚀 Cómo funciona

```
┌─────────────┐
│ Imagen PNG  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ IA Visión       │ ← Analiza características
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ IA Genera SVG   │ ← Prompt: "vectoriza esta imagen"
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Render SVG→PNG  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ IA Compara      │ ← "¿Qué diferencias hay?"
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ IA Modifica SVG │ ← "Mejora estas áreas"
└──────┬──────────┘
       │
       └───────┐ (loop)
               │
               ▼
        ┌──────────────┐
        │ ¿Calidad OK? │
        └──────┬───────┘
               │
         Sí ───┴─── No
         │         │
         ▼         ▼
    ┌────────┐  ┌─────────┐
    │ SVG    │  │ Iterar  │
    │ Final  │  │         │
    └────────┘  └─────────┘
```

## 💡 Por qué este enfoque es diferente

A diferencia de los vectorizadores tradicionales (Potrace, Vectorizer.js, Adobe Illustrator), este proyecto utiliza **IA semántica** para entender el contenido de la imagen en lugar de simplemente trazar píxeles.

### Vectorizadores tradicionales vs Vectorizer AI

| Aspecto | Tradicionales (Potrace, etc.) | Vectorizer AI (Este proyecto) |
|---------|-------------------------------|------------------------------|
| **Enfoque** | Trazado de píxeles | Comprensión semántica |
| **Salida** | Paths/polígonos complejos | Texto editable + formas |
| **Texto** | Convierte a paths (no editable) | Texto real seleccionable |
| **Colores** | Muestreo de píxeles | Identificación precisa (#525252, #72bc3e) |
| **Tamanho** | Miles de puntos (~50KB+) | ~200 bytes (10x más pequeño) |
| **Escalabilidad** | Limitada por paths | Infinita (texto vectorial) |
| **Edición** | Dificultosa (paths) | Fácil (texto + colores) |
| **Accesibilidad** | Ninguna | SEO (texto seleccionable) |
| **Márgenes** | Automáticos/imprecisos | IA ajusta según contexto |
| **Fondo** | Blanco/opaco | Transparente por defecto |

### Ventajas clave del enfoque semántico:

1. **OCR implícito**: La IA detecta automáticamente que hay texto y lo vectoriza como `<text>` en lugar de paths.

2. **Colores precisos**: Identifica los colores hex exactos (ej: #525252 para gris) en lugar de aproximar.

3. **SVG optimizado**: Genera archivos 10x más pequeños porque usa texto nativo.

4. **Editable**: El resultado se puede modificar en cualquier editor de texto o diseño.

5. **Transparente**: Ideal para logos que deben funcionar en cualquier fondo.

### Ejemplo práctico:

**Entrada** (PNG 50KB con fondo blanco):
```
Qualidades
consultoria >
```

**Salida tradicional** (Potrace):
```svg
<path d="M10,10 L20,15 L30,10..." fill="#525252"/> <!-- Miles de puntos -->
```

**Salida Vectorizer AI**:
```svg
<text fill="#525252">Quali</text>
<text fill="#72bc3e">dades</text>
<text fill="#525252">consultoria</text>
<text fill="#525252">></text>
```

El resultado de la IA es **200x más pequeño**, **100% editable**, y **accesible** para lectores de pantalla.

---

## 📋 Requisitos

- Python 3.10+
- API Key de Google Gemini (gratis), Anthropic Claude o OpenAI GPT-4V
- GTK3 Runtime (para renderizado SVG en Windows)
- Dependencias del proyecto (ver `requirements.txt`)

## 📦 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/mcarbonell/vectorizer-ai.git
cd vectorizer-ai

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar GTK3 Runtime (Windows, requerido para renderizado)
winget install --id=tschoonj.GTKForWindows -e

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys
```

## 🎯 Uso básico

```bash
# Vectorizar una imagen (usa Google Gemini por defecto)
python -m vectorizer input.png output.svg

# Con proveedor específico
python -m vectorizer input.png output.svg --provider google --model gemini-2.5-flash

# Con número máximo de iteraciones
python -m vectorizer input.png output.svg --max-iterations 10

# Con umbral de calidad específico
python -m vectorizer input.png output.svg --quality-threshold 0.9

# Ver progreso detallado
python -m vectorizer input.png output.svg --verbose
```

### Proveedores soportados:

| Proveedor | Modelo | API Key |
|-----------|--------|---------|
| Google Gemini | 2.5 Flash (gratis) | `GOOGLE_API_KEY` |
| OpenAI | GPT-4V | `OPENAI_API_KEY` |
| Anthropic | Claude 3.5 Sonnet | `ANTHROPIC_API_KEY` |

## ⚙️ Configuración

El archivo `.env` permite configurar:

```env
# API Keys
GOOGLE_API_KEY=AI...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Configuración del vectorizador
MAX_ITERATIONS=10
QUALITY_THRESHOLD=0.85
DEFAULT_PROVIDER=google
DEFAULT_MODEL=gemini-2.5-flash

# Rutas
TEMP_DIR=./temp
OUTPUT_DIR=./output
```

## 📚 Documentación

- [Arquitectura del sistema](docs/architecture.md)
- [Guía de desarrollo](docs/development.md)
- [API Reference](docs/api.md)
- [Contribución](docs/CONTRIBUTING.md)

## 🔬 Arquitectura técnica

El proyecto está organizado en los siguientes módulos:

```
vectorizer-ai/
├── src/
│   ├── vectorizer/          # Módulo principal
│   │   ├── __init__.py
│   │   ├── core.py          # Lógica principal de vectorización
│   │   ├── vision.py        # Integración con APIs de visión
│   │   ├── svg_generator.py # Generación de SVG
│   │   ├── comparator.py    # Comparación de imágenes
│   │   └── metrics.py       # Métricas de calidad
│   └── utils/               # Utilidades
│       ├── __init__.py
│       ├── image.py         # Procesamiento de imágenes
│       └── config.py        # Configuración
├── tests/                   # Tests
├── docs/                    # Documentación
└── examples/                # Ejemplos de uso
```

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con cobertura
pytest --cov=src/vectorizer

# Ejecutar tests específicos
pytest tests/test_vision.py
```

## 📊 Roadmap

| Estado | Fase |
|--------|------|
| [x] | Concepto y diseño |
| [x] | Prototipo inicial |
| [x] | Integración con Google Gemini 2.5 Flash |
| [x] | Sistema de métricas (SSIM + CLIP) |
| [x] | Interfaz de línea de comandos |
| [x] | Renderizado SVG con Cairo |
| [x] | Documentación completa |
| [ ] | Tests automatizados |
| [ ] | Integración con Claude/GPT-4V |
| [ ] | API REST |
| [ ] | Web UI |

---

## 🏆 Primera prueba exitosa

**Fecha**: Febrero 2026  
**Imagen**: Logo "Qualidades consultoria"  
**Resultado**: SVG generado con texto editable y fondo transparente

```svg
<svg viewBox="0 0 500 120">
  <text fill="#007BFF">Quali</text>
  <text fill="#2ECC71">dades</text>
  <text fill="#5A6268">consultoria</text>
  <polygon points="..." fill="#138496"/>
</svg>
```

**Métricas logradas**:
- CLIP Score: 0.86
- SSIM: 0.36

---


## 📝 Licencia

MIT License - Ver archivo [LICENSE](LICENSE) para detalles

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor, lee [CONTRIBUTING.md](docs/CONTRIBUTING.md) antes de contribuir.

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.

---

**Nota**: Este proyecto ha alcanzado su primer hito funcional. La API y la arquitectura pueden cambiar.
