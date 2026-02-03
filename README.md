# 🎨 Vectorizer AI

Un vectorizador de imágenes impulsado por inteligencia artificial que utiliza visión por computadora y generación de código iterativa para convertir imágenes rasterizadas (PNG, JPG) en gráficos vectoriales (SVG) de alta calidad.

## 🌟 Características

- **Vectorización basada en IA**: Utiliza modelos de visión para analizar y comparar imágenes
- **Optimización iterativa**: Proceso de refinamiento continuo hasta alcanzar la calidad deseada
- **Comparación visual**: La IA "ve" las diferencias entre el original y el SVG generado
- **Sin entrenamiento**: Aprovecha modelos pre-entrenados (Claude, GPT-4V, etc.)
- **Múltiples formatos de entrada**: Soporta PNG, JPG, WEBP y más
- **Salida SVG optimizada**: Genera SVGs limpios y editables

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

## 📋 Requisitos

- Python 3.10+
- API key de Claude (Anthropic) o GPT-4V (OpenAI)
- Dependencias del proyecto (ver `requirements.txt`)

## 📦 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/vectorizer-ai.git
cd vectorizer-ai

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys
```

## 🎯 Uso básico

```bash
# Vectorizar una imagen
python -m vectorizer input.png output.svg

# Con número máximo de iteraciones
python -m vectorizer input.png output.svg --max-iterations 10

# Con umbral de calidad específico
python -m vectorizer input.png output.svg --quality-threshold 0.9

# Ver progreso detallado
python -m vectorizer input.png output.svg --verbose
```

## ⚙️ Configuración

El archivo `.env` permite configurar:

```env
# API Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Configuración del vectorizador
MAX_ITERATIONS=10
QUALITY_THRESHOLD=0.85
DEFAULT_MODEL=claude-3-5-sonnet-20241022

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

- [x] Concepto y diseño
- [ ] Prototipo inicial
- [ ] Integración con APIs de IA
- [ ] Sistema de métricas de calidad
- [ ] Interfaz de línea de comandos
- [ ] Documentación completa
- [ ] Tests automatizados

## 📝 Licencia

MIT License - Ver archivo [LICENSE](LICENSE) para detalles

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor, lee [CONTRIBUTING.md](docs/CONTRIBUTING.md) antes de contribuir.

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.

---

**Nota**: Este proyecto está en fase de desarrollo activo. La API y la arquitectura pueden cambiar.
