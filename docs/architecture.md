# Arquitectura del Sistema

## Visión General

Vectorizer AI utiliza un enfoque iterativo de optimización basado en visión para convertir imágenes rasterizadas en gráficos vectoriales de alta calidad.

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Interface                            │
│                    (vectorizer command)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Vectorizer Core                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Orchestr   │  │   Metrics    │  │   Config     │          │
│  │   ator       │  │   Engine     │  │   Manager    │          │
│  └──────┬───────┘  └──────────────┘  └──────────────┘          │
└─────────┼───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Vision & AI Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Vision     │  │   SVG        │  │   Image      │          │
│  │   Analyzer   │  │   Generator  │  │   Comparator │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External APIs                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Anthropic  │  │   OpenAI     │  │   Other      │          │
│  │   (Claude)   │  │   (GPT-4V)   │  │   APIs       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Componentes Principales

### 1. CLI Interface
- **Responsabilidad**: Punto de entrada del usuario
- **Funciones**:
  - Parseo de argumentos
  - Validación de entrada
  - Visualización de progreso
  - Manejo de errores

### 2. Vectorizer Core

#### 2.1 Orchestrator
- **Responsabilidad**: Coordinar el flujo de vectorización
- **Funciones**:
  - Gestionar el ciclo iterativo
  - Controlar el número de iteraciones
  - Decidir cuándo detenerse
  - Orquestar llamadas a otros componentes

#### 2.2 Metrics Engine
- **Responsabilidad**: Calcular métricas de calidad
- **Funciones**:
  - SSIM (Structural Similarity Index)
  - LPIPS (Learned Perceptual Image Patch Similarity)
  - CLIP Similarity
  - Métricas personalizadas

#### 2.3 Config Manager
- **Responsabilidad**: Gestionar configuración
- **Funciones**:
  - Cargar configuración desde archivos
  - Validar parámetros
  - Proveer valores por defecto

### 3. Vision & AI Layer

#### 3.1 Vision Analyzer
- **Responsabilidad**: Analizar imágenes con IA
- **Funciones**:
  - Extraer características visuales
  - Identificar elementos clave
  - Describir contenido
  - Detectar colores y formas

#### 3.2 SVG Generator
- **Responsabilidad**: Generar código SVG
- **Funciones**:
  - Crear SVG inicial
  - Modificar SVG existente
  - Optimizar código SVG
  - Validar sintaxis SVG

#### 3.3 Image Comparator
- **Responsabilidad**: Comparar imágenes visualmente
- **Funciones**:
  - Renderizar SVG a PNG
  - Comparar con original
  - Identificar diferencias
  - Generar reporte de mejoras

### 4. External APIs
- **Anthropic Claude**: Visión y generación de código
- **OpenAI GPT-4V**: Visión y análisis
- **Otros**: APIs alternativas o futuras

## Flujo de Trabajo Detallado

### Fase 1: Análisis Inicial
```
1. Cargar imagen original
2. Vision Analyzer analiza la imagen
   - Identifica formas principales
   - Detecta paleta de colores
   - Describe composición
   - Extrae características clave
3. Guardar análisis para referencia
```

### Fase 2: Generación Inicial
```
1. SVG Generator crea SVG inicial
   - Basado en análisis de Vision Analyzer
   - Usa prompt optimizado
   - Genera estructura básica
2. Validar SVG generado
3. Renderizar SVG a PNG
```

### Fase 3: Comparación y Evaluación
```
1. Image Comparator compara:
   - PNG original vs PNG renderizado
   - Calcula métricas de similitud
   - Identifica áreas problemáticas
2. Metrics Engine calcula:
   - SSIM score
   - CLIP similarity
   - Puntuación de calidad global
3. Evaluar si cumple umbral
```

### Fase 4: Refinamiento Iterativo
```
Mientras (iteraciones < max_iteraciones AND calidad < umbral):
  1. Vision Analyzer identifica diferencias
  2. SVG Generator modifica SVG
     - Ajusta colores
     - Refina formas
     - Mejora detalles
  3. Renderizar SVG a PNG
  4. Comparar y evaluar
  5. Si mejora, guardar; si no, revertir
```

### Fase 5: Finalización
```
1. Seleccionar mejor SVG
2. Optimizar SVG final
   - Minificar código
   - Optimizar rutas
   - Comprimir si es necesario
3. Guardar SVG final
4. Generar reporte de calidad
```

## Modelos de Datos

### ImageAnalysis
```python
{
    "shapes": ["circle", "rectangle", "path"],
    "colors": ["#FF0000", "#00FF00", "#0000FF"],
    "composition": "centered",
    "complexity": "medium",
    "style": "flat",
    "description": "..."
}
```

### SVGGeneration
```python
{
    "svg_code": "<svg>...</svg>",
    "metadata": {
        "elements_count": 5,
        "paths_count": 3,
        "file_size": 1024
    }
}
```

### ComparisonResult
```python
{
    "ssim": 0.85,
    "clip_similarity": 0.92,
    "quality_score": 0.88,
    "differences": [
        {"area": "top_left", "issue": "color_mismatch"},
        {"area": "center", "issue": "shape_precision"}
    ]
}
```

### IterationResult
```python
{
    "iteration": 3,
    "svg": "<svg>...</svg>",
    "quality": 0.88,
    "improvement": 0.05,
    "metrics": {...}
}
```

## Estrategias de Optimización

### 1. Prompt Engineering
- Prompts específicos para cada fase
- Contexto acumulado entre iteraciones
- Ejemplos few-shot cuando sea posible

### 2. Early Stopping
- Detener si no hay mejora en N iteraciones
- Detener si calidad supera umbral
- Límite máximo de iteraciones

### 3. Caching
- Cachear respuestas de API
- Reutilizar análisis de visión
- Guardar renderizados intermedios

### 4. Paralelización (futuro)
- Múltiples variantes en paralelo
- Selección del mejor resultado
- Ensemble de modelos

## Manejo de Errores

### Errores de API
- Reintentos con backoff exponencial
- Fallback a API alternativa
- Timeout handling

### Errores de SVG
- Validación antes de renderizar
- Sanitización de SVG malformado
- Fallback a versión anterior

### Errores de Calidad
- Detección de degradación
- Revertir a mejor versión anterior
- Alertas al usuario

## Consideraciones de Rendimiento

### Costos de API
- Estimar costos por iteración
- Límites de tokens
- Optimización de prompts

### Tiempo de Ejecución
- Tiempo estimado por iteración
- Progreso visual para el usuario
- Cancelación graceful

### Uso de Memoria
- Gestión de imágenes temporales
- Limpieza de caché
- Streaming de archivos grandes

## Seguridad

### Validación de Entrada
- Sanitización de rutas de archivo
- Límites de tamaño de imagen
- Validación de formatos

### Protección de API Keys
- Variables de entorno
- Nunca en código
- Rotación de keys

### SVG Seguro
- Sanitización de SVG generado
- Prevención de XSS
- Validación de contenido

## Extensibilidad

### Nuevos Modelos de IA
- Interfaz abstracta para APIs
- Fácil agregar nuevos proveedores
- Configuración por modelo

### Nuevas Métricas
- Sistema de plugins para métricas
- Métricas personalizadas
- Combinación de métricas

### Nuevos Formatos
- Soporte para más formatos de entrada
- Exportación a otros formatos vectoriales
- Conversión entre formatos
