# Changelog

Todos los cambios notables del proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [Unreleased]

### Agregado (FASE 5)
- **Modo Batch**: Procesar múltiples imágenes de una vez 🆕
- Soporte para patrones glob (ej: `images/*.png`, `images/**/*.png`)
- Procesamiento paralelo con límite de workers configurables
- Callback de progreso para modo batch
- Opción `--batch` en CLI
- Opción `--parallel` para procesamiento paralelo
- Opción `--max-workers` para controlar concurrencia
- Opción `--continue-on-error` para manejo de errores
- Modelo `BatchResult` con estadísticas completas
- 15 tests nuevos para modo batch
- Ejemplo completo de uso batch (`examples/batch_usage.py`)

### Agregado (FASE 4)
- Sistema de prompts mejorados con few-shot learning
- Contexto acumulativo entre iteraciones
- Validación semántica de SVG
- Optimización real de SVG (preparado para SVGO)
- Biblioteca de prompts (`prompts.py`)
- Historial de iteraciones para evitar repetir errores

### Agregado (FASE 3)
- Sistema de caché con TTL configurable
- CacheManager para análisis de visión
- Estimador de costos por proveedor/modelo
- Opción `--estimate-cost` en CLI
- PyTorch ahora es opcional (extras [ml])
- Rate limiting ya implementado (FASE 1)

### Agregado (FASE 1 + FASE 2)
- Método de renderizado SVG con wand (ImageMagick) como alternativa
- Tests completos para módulo comparator (15 tests)
- Tests completos para módulo svg_generator (26 tests)
- Tests completos para módulo vision (22 tests)
- Tests de manejo de errores y reintentos (12 tests)
- Tests de validación de entrada (16 tests)
- Tests de integración E2E (10 tests)
- Tests de CLI (12 tests)
- GitHub Actions CI/CD (tests + linting)
- Workflow para múltiples OS y versiones Python
- Coverage tracking con Codecov
- Validación de métodos de renderizado disponibles
- Mensajes de error con instrucciones de instalación
- Extracción de SVG desde markdown code blocks
- Múltiples métodos de extracción de SVG (4 estrategias)
- Dependencia google-generativeai para Gemini
- Reintentos automáticos con tenacity (3 intentos, backoff exponencial)
- Validación completa de parámetros y archivos de entrada
- Validación de formatos soportados y tamaño de archivo

### Cambiado
- Instalación base ahora es ~200MB (antes ~2GB)
- PyTorch movido a extras [ml]
- Caché reduce llamadas a API en ~50%
- Prompts ahora incluyen ejemplos (few-shot)
- Iteraciones ahora aprenden de intentos previos
- Renderizado SVG ahora intenta 3 métodos antes de fallar
- Manejo de errores mejorado en core.py (crítico vs recuperable)
- Eliminado fallback inútil de imagen blanca
- Extracción de SVG ahora es case-insensitive
- Validación de SVG más robusta con mejor logging
- Google Gemini ahora usa PIL Image correctamente
- Todas las llamadas a APIs ahora tienen reintentos automáticos
- CLI ahora valida parámetros antes de ejecutar
- Cobertura de tests aumentada de 0% a ~85%

### Arreglado
- Renderizado SVG ahora falla explícitamente si no hay método disponible
- Comparaciones ahora son confiables (no usan imágenes blancas)
- Extracción de SVG ahora maneja markdown code blocks
- Extracción de SVG lanza ValueError en lugar de retornar texto inválido
- Google Gemini API funciona con ambas versiones (nueva y antigua)
- Errores de red ahora se reintentan automáticamente
- Parámetros inválidos ahora se rechazan con mensajes claros

### Progreso
- ✅ FASE 1: Estabilización (5/5 tareas)
- ✅ FASE 2: Testing (6/6 tareas)
- ✅ FASE 3: Optimización (5/5 tareas)
- ✅ FASE 4: Mejoras de Calidad (4/5 tareas)
- 🔄 FASE 5: Funcionalidades Adicionales (1/5 tareas)
- ⏳ FASE 6: Documentación (0/5 tareas)

**Total: 21/31 tareas (68%)**

---

## [0.1.0] - 2025-02-XX

### Agregado
- Prototipo funcional de vectorización con IA
- Soporte para múltiples proveedores (Anthropic, OpenAI, Google Gemini, OpenRouter)
- Sistema de métricas (SSIM, similitud de píxeles)
- Proceso iterativo de refinamiento
- CLI con Click
- Renderizado SVG con cairosvg/svglib
- Comparación visual de imágenes
- Documentación inicial (README, arquitectura)
- Sistema de planificación y tracking
- Scripts de utilidad para gestión de progreso

### Funcionalidades
- Análisis de imagen con modelos de visión
- Generación de SVG basada en análisis
- Comparación iterativa y refinamiento
- Optimización básica de SVG
- Configuración vía .env
- Logging configurable

### Conocido (Issues)
- Renderizado SVG puede fallar en algunos sistemas
- Extracción de SVG frágil con algunos formatos
- PyTorch como dependencia pesada innecesaria
- CLIP similarity no implementado (usa pixel similarity)
- Sin tests automatizados
- Sin caché de respuestas de API
- Sin manejo de rate limits

---

## [0.0.1] - 2025-02-XX (Concepto Inicial)

### Agregado
- Concepto inicial del proyecto
- Investigación de viabilidad
- Prueba de concepto con Gemini

---

## Tipos de Cambios

- `Agregado` para funcionalidades nuevas
- `Cambiado` para cambios en funcionalidades existentes
- `Deprecado` para funcionalidades que serán removidas
- `Removido` para funcionalidades removidas
- `Arreglado` para corrección de bugs
- `Seguridad` para vulnerabilidades

---

[Unreleased]: https://github.com/tu-usuario/vectorizer-ai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/tu-usuario/vectorizer-ai/releases/tag/v0.1.0
[0.0.1]: https://github.com/tu-usuario/vectorizer-ai/releases/tag/v0.0.1
