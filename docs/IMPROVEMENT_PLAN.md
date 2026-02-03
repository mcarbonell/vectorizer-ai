# 🚀 Plan de Mejoras - Vectorizer AI

**Fecha de creación**: Febrero 2025  
**Estado**: En progreso  
**Versión actual**: 0.1.0  
**Versión objetivo**: 0.2.0

---

## 📋 Resumen Ejecutivo

Este documento detalla el plan de mejoras para llevar Vectorizer AI de un prototipo funcional a una herramienta production-ready. Las mejoras están organizadas por prioridad y estimación de esfuerzo.

**Métricas objetivo**:
- ✅ Cobertura de tests: 0% → 80%
- ✅ Tamaño de instalación: ~2GB → ~200MB
- ✅ Tasa de éxito de renderizado: ~60% → 95%
- ✅ Tiempo de ejecución: Reducir 30% con caché

---

## 🎯 Fases de Implementación

### **FASE 1: Estabilización (Crítico)** 🔴
**Objetivo**: Hacer que el sistema funcione de forma confiable  
**Duración estimada**: 2-3 días  
**Estado**: ⏳ Pendiente

| # | Tarea | Prioridad | Esfuerzo | Estado |
|---|-------|-----------|----------|--------|
| 1.1 | Arreglar renderizado SVG | 🔴 Alta | 2h | ✅ Completado |
| 1.2 | Mejorar extracción de SVG | 🔴 Alta | 1h | ✅ Completado |
| 1.3 | Arreglar Google Gemini API | 🔴 Alta | 1h | ✅ Completado |
| 1.4 | Manejo robusto de errores | 🔴 Alta | 2h | ✅ Completado |
| 1.5 | Validación de entrada | 🔴 Alta | 1h | ✅ Completado |

---

### **FASE 2: Testing (Crítico)** 🔴
**Objetivo**: Agregar cobertura de tests para validar funcionalidad  
**Duración estimada**: 2-3 días  
**Estado**: ⏳ Pendiente

| # | Tarea | Prioridad | Esfuerzo | Estado |
|---|-------|-----------|----------|--------|
| 2.1 | Tests unitarios - VisionAnalyzer | 🔴 Alta | 2h | ⏳ Pendiente |
| 2.2 | Tests unitarios - SVGGenerator | 🔴 Alta | 2h | ⏳ Pendiente |
| 2.3 | Tests unitarios - ImageComparator | 🔴 Alta | 2h | ⏳ Pendiente |
| 2.4 | Tests de integración - Core | 🔴 Alta | 3h | ⏳ Pendiente |
| 2.5 | Tests de CLI | 🟡 Media | 1h | ⏳ Pendiente |
| 2.6 | Configurar CI/CD básico | 🟡 Media | 2h | ⏳ Pendiente |

---

### **FASE 3: Optimización (Importante)** 🟡
**Objetivo**: Mejorar rendimiento y reducir costos  
**Duración estimada**: 2-3 días  
**Estado**: ⏳ Pendiente

| # | Tarea | Prioridad | Esfuerzo | Estado |
|---|-------|-----------|----------|--------|
| 3.1 | Implementar sistema de caché | 🟡 Media | 3h | ⏳ Pendiente |
| 3.2 | Hacer PyTorch opcional | 🟡 Media | 1h | ⏳ Pendiente |
| 3.3 | Optimizar dependencias | 🟡 Media | 2h | ⏳ Pendiente |
| 3.4 | Implementar rate limiting | 🟡 Media | 2h | ⏳ Pendiente |
| 3.5 | Estimador de costos | 🟡 Media | 2h | ⏳ Pendiente |

---

### **FASE 4: Mejoras de Calidad (Importante)** 🟡
**Objetivo**: Mejorar la calidad de los SVGs generados  
**Duración estimada**: 3-4 días  
**Estado**: ⏳ Pendiente

| # | Tarea | Prioridad | Esfuerzo | Estado |
|---|-------|-----------|----------|--------|
| 4.1 | Mejorar prompts con few-shot | 🟡 Media | 3h | ⏳ Pendiente |
| 4.2 | Contexto acumulativo | 🟡 Media | 2h | ⏳ Pendiente |
| 4.3 | Validación semántica de SVG | 🟡 Media | 2h | ⏳ Pendiente |
| 4.4 | Optimización real de SVG (SVGO) | 🟡 Media | 2h | ⏳ Pendiente |
| 4.5 | Implementar CLIP real | 🟢 Baja | 3h | ⏳ Pendiente |

---

### **FASE 5: Funcionalidades Adicionales (Opcional)** 🟢
**Objetivo**: Agregar features que mejoren la experiencia  
**Duración estimada**: 4-5 días  
**Estado**: ⏳ Pendiente

| # | Tarea | Prioridad | Esfuerzo | Estado |
|---|-------|-----------|----------|--------|
| 5.1 | Modo batch (múltiples imágenes) | 🟢 Baja | 3h | ⏳ Pendiente |
| 5.2 | Exportar reporte de calidad | 🟢 Baja | 2h | ⏳ Pendiente |
| 5.3 | Comparación visual (HTML) | 🟢 Baja | 3h | ⏳ Pendiente |
| 5.4 | Configuración por archivo | 🟢 Baja | 2h | ⏳ Pendiente |
| 5.5 | Logging estructurado | 🟢 Baja | 2h | ⏳ Pendiente |

---

### **FASE 6: Documentación y Pulido (Opcional)** 🟢
**Objetivo**: Mejorar documentación y experiencia de usuario  
**Duración estimada**: 2-3 días  
**Estado**: ⏳ Pendiente

| # | Tarea | Prioridad | Esfuerzo | Estado |
|---|-------|-----------|----------|--------|
| 6.1 | Actualizar README con ejemplos | 🟢 Baja | 2h | ⏳ Pendiente |
| 6.2 | Guía de troubleshooting | 🟢 Baja | 2h | ⏳ Pendiente |
| 6.3 | Documentación de API | 🟢 Baja | 3h | ⏳ Pendiente |
| 6.4 | Video tutorial | 🟢 Baja | 4h | ⏳ Pendiente |
| 6.5 | Galería de ejemplos | 🟢 Baja | 2h | ⏳ Pendiente |

---

## 📝 Detalle de Tareas

### **FASE 1: Estabilización**

#### **1.1 Arreglar renderizado SVG** 🔴
**Problema**: Fallback a imagen blanca hace comparaciones inútiles  
**Archivos**: `src/vectorizer/comparator.py`

**Cambios necesarios**:
- [ ] Agregar método con Playwright/Selenium como fallback
- [ ] Validar instalación de GTK3 en Windows
- [ ] Agregar instrucciones claras de instalación
- [ ] Fallar explícitamente si no hay método disponible
- [ ] Agregar tests de renderizado

**Criterios de aceptación**:
- ✅ Renderizado funciona en Windows con GTK3
- ✅ Fallback funcional si cairosvg falla
- ✅ Error claro si no hay método disponible
- ✅ Tests pasan en CI

---

#### **1.2 Mejorar extracción de SVG** 🔴
**Problema**: Regex frágil, no maneja markdown code blocks  
**Archivos**: `src/vectorizer/svg_generator.py`

**Cambios necesarios**:
- [ ] Detectar y extraer de markdown code blocks (```svg)
- [ ] Parser más robusto con múltiples estrategias
- [ ] Validación de SVG extraído
- [ ] Logging de qué método funcionó
- [ ] Tests con diferentes formatos de respuesta

**Criterios de aceptación**:
- ✅ Extrae SVG de markdown code blocks
- ✅ Extrae SVG de respuestas sin formato
- ✅ Maneja SVGs anidados
- ✅ Tests cubren casos edge

---

#### **1.3 Arreglar Google Gemini API** 🔴
**Problema**: Pasa string en lugar de objeto Image  
**Archivos**: `src/vectorizer/vision.py`

**Cambios necesarios**:
- [ ] Usar PIL Image correctamente con Gemini
- [ ] Validar con ambas APIs (nueva y antigua)
- [ ] Agregar tests específicos para Gemini
- [ ] Documentar diferencias entre APIs

**Criterios de aceptación**:
- ✅ Funciona con google.genai (nueva API)
- ✅ Funciona con google.generativeai (antigua API)
- ✅ Tests pasan con ambas versiones
- ✅ Documentación actualizada

---

#### **1.4 Manejo robusto de errores** 🔴
**Problema**: Errores silenciosos, continúa sin validar  
**Archivos**: `src/vectorizer/core.py`, todos los módulos

**Cambios necesarios**:
- [ ] Implementar reintentos con tenacity
- [ ] Estrategia de recuperación clara
- [ ] Logging estructurado de errores
- [ ] Mensajes de error útiles para el usuario
- [ ] Tests de manejo de errores

**Criterios de aceptación**:
- ✅ Reintentos automáticos con backoff
- ✅ Errores claros y accionables
- ✅ No continúa con datos inválidos
- ✅ Tests de error handling

---

#### **1.5 Validación de entrada** 🔴
**Problema**: Poca validación de archivos y parámetros  
**Archivos**: `src/vectorizer/core.py`, `src/vectorizer/cli.py`

**Cambios necesarios**:
- [ ] Validar formato de imagen soportado
- [ ] Validar tamaño de imagen (límite)
- [ ] Validar parámetros (iteraciones, threshold)
- [ ] Validar API keys antes de empezar
- [ ] Tests de validación

**Criterios de aceptación**:
- ✅ Rechaza formatos no soportados
- ✅ Rechaza imágenes muy grandes
- ✅ Valida parámetros en rango correcto
- ✅ Tests de validación

---

### **FASE 2: Testing**

#### **2.1-2.3 Tests unitarios** 🔴
**Archivos**: `tests/test_vision.py`, `tests/test_svg_generator.py`, `tests/test_comparator.py`

**Tests necesarios**:
- [ ] VisionAnalyzer: análisis de imagen, parseo de respuesta, manejo de errores
- [ ] SVGGenerator: generación, modificación, optimización, extracción
- [ ] ImageComparator: comparación, renderizado, métricas, diferencias

**Criterios de aceptación**:
- ✅ Cobertura > 80% por módulo
- ✅ Tests pasan en CI
- ✅ Mocks de APIs funcionan

---

#### **2.4 Tests de integración** 🔴
**Archivos**: `tests/test_integration.py`

**Tests necesarios**:
- [ ] Flujo completo end-to-end
- [ ] Múltiples iteraciones
- [ ] Diferentes proveedores
- [ ] Manejo de errores en flujo completo

**Criterios de aceptación**:
- ✅ Test E2E pasa con imagen de prueba
- ✅ Tests con diferentes proveedores
- ✅ Tests de error recovery

---

#### **2.5 Tests de CLI** 🟡
**Archivos**: `tests/test_cli.py`

**Tests necesarios**:
- [ ] Argumentos válidos
- [ ] Argumentos inválidos
- [ ] Variables de entorno
- [ ] Output esperado

**Criterios de aceptación**:
- ✅ CLI tests pasan
- ✅ Validación de argumentos funciona

---

#### **2.6 CI/CD básico** 🟡
**Archivos**: `.github/workflows/test.yml`

**Configuración necesaria**:
- [ ] GitHub Actions para tests
- [ ] Tests en Python 3.10, 3.11, 3.12
- [ ] Linting con flake8/black
- [ ] Coverage report

**Criterios de aceptación**:
- ✅ CI corre en cada PR
- ✅ Tests pasan en múltiples versiones
- ✅ Coverage visible

---

### **FASE 3: Optimización**

#### **3.1 Sistema de caché** 🟡
**Archivos**: `src/vectorizer/cache.py`, actualizar módulos

**Implementación**:
- [ ] CacheManager con hash de imagen + modelo
- [ ] Caché de análisis de visión
- [ ] Caché de generaciones de SVG
- [ ] TTL configurable
- [ ] Limpieza de caché antiguo

**Criterios de aceptación**:
- ✅ Caché funciona correctamente
- ✅ Reduce tiempo de ejecución 30%
- ✅ Configurable vía .env
- ✅ Tests de caché

---

#### **3.2 PyTorch opcional** 🟡
**Archivos**: `requirements.txt`, `pyproject.toml`, `src/vectorizer/metrics.py`

**Cambios**:
- [ ] Mover PyTorch a extras_require
- [ ] Importación condicional en metrics.py
- [ ] Fallback sin PyTorch
- [ ] Documentar instalación opcional

**Criterios de aceptación**:
- ✅ Instalación base < 300MB
- ✅ Funciona sin PyTorch
- ✅ Documentación clara

---

#### **3.3 Optimizar dependencias** 🟡
**Archivos**: `requirements.txt`, `pyproject.toml`

**Revisión**:
- [ ] Eliminar dependencias no usadas
- [ ] Versiones mínimas necesarias
- [ ] Agrupar por categoría
- [ ] Documentar para qué sirve cada una

**Criterios de aceptación**:
- ✅ Solo dependencias necesarias
- ✅ Instalación más rápida
- ✅ Documentación actualizada

---

#### **3.4 Rate limiting** 🟡
**Archivos**: `src/vectorizer/vision.py`, `src/vectorizer/svg_generator.py`

**Implementación**:
- [ ] Usar tenacity para reintentos
- [ ] Backoff exponencial
- [ ] Límites por proveedor
- [ ] Logging de reintentos

**Criterios de aceptación**:
- ✅ Maneja rate limits automáticamente
- ✅ No falla por límites temporales
- ✅ Tests de rate limiting

---

#### **3.5 Estimador de costos** 🟡
**Archivos**: `src/vectorizer/cost_estimator.py`, actualizar CLI

**Implementación**:
- [ ] Calcular tokens estimados
- [ ] Costos por proveedor
- [ ] Mostrar estimación antes de ejecutar
- [ ] Opción --dry-run

**Criterios de aceptación**:
- ✅ Estimación razonable de costos
- ✅ Mostrado en CLI
- ✅ Documentación de costos

---

### **FASE 4: Mejoras de Calidad**

#### **4.1 Prompts con few-shot** 🟡
**Archivos**: `src/vectorizer/vision.py`, `src/vectorizer/svg_generator.py`

**Mejoras**:
- [ ] Agregar ejemplos en prompts
- [ ] Prompts específicos por tipo de imagen
- [ ] Biblioteca de prompts
- [ ] A/B testing de prompts

**Criterios de aceptación**:
- ✅ Mejora calidad de SVG generado
- ✅ Prompts documentados
- ✅ Tests con diferentes prompts

---

#### **4.2 Contexto acumulativo** 🟡
**Archivos**: `src/vectorizer/core.py`

**Implementación**:
- [ ] Mantener historial de iteraciones
- [ ] Pasar contexto a modificaciones
- [ ] Aprender de errores anteriores
- [ ] Evitar repetir cambios fallidos

**Criterios de aceptación**:
- ✅ Iteraciones más efectivas
- ✅ Menos iteraciones necesarias
- ✅ Tests de contexto

---

#### **4.3 Validación semántica** 🟡
**Archivos**: `src/vectorizer/svg_generator.py`

**Implementación**:
- [ ] Validar que SVG tiene elementos esperados
- [ ] Validar colores vs análisis
- [ ] Validar complejidad apropiada
- [ ] Score de validación

**Criterios de aceptación**:
- ✅ Detecta SVGs de baja calidad
- ✅ Rechaza SVGs inválidos
- ✅ Tests de validación

---

#### **4.4 Optimización real (SVGO)** 🟡
**Archivos**: `src/vectorizer/svg_generator.py`

**Implementación**:
- [ ] Integrar SVGO o svgo-python
- [ ] Optimización configurable
- [ ] Preservar calidad visual
- [ ] Comparar antes/después

**Criterios de aceptación**:
- ✅ SVGs más pequeños (30-50%)
- ✅ Sin pérdida de calidad
- ✅ Tests de optimización

---

#### **4.5 CLIP real** 🟢
**Archivos**: `src/vectorizer/metrics.py`

**Implementación**:
- [ ] Integrar transformers + CLIP
- [ ] Embeddings de imágenes
- [ ] Similitud coseno
- [ ] Opcional (dependencia pesada)

**Criterios de aceptación**:
- ✅ CLIP funciona correctamente
- ✅ Mejora métricas de calidad
- ✅ Documentado como opcional

---

### **FASE 5 y 6**: Ver documento para detalles completos

---

## 📊 Métricas de Progreso

### Progreso General
```
FASE 1: [░░░░░░░░░░] 0/5 tareas (0%)
FASE 2: [░░░░░░░░░░] 0/6 tareas (0%)
FASE 3: [░░░░░░░░░░] 0/5 tareas (0%)
FASE 4: [░░░░░░░░░░] 0/5 tareas (0%)
FASE 5: [░░░░░░░░░░] 0/5 tareas (0%)
FASE 6: [░░░░░░░░░░] 0/5 tareas (0%)

TOTAL: [░░░░░░░░░░] 0/31 tareas (0%)
```

### Cobertura de Tests
```
Actual:    [░░░░░░░░░░] 0%
Objetivo:  [████████░░] 80%
```

### Tamaño de Instalación
```
Actual:    [██████████] ~2GB
Objetivo:  [██░░░░░░░░] ~200MB
```

---

## 🎯 Próximos Pasos

### Inmediatos (Esta semana)
1. ✅ Crear este documento de planificación
2. ⏳ Comenzar FASE 1.1: Arreglar renderizado SVG
3. ⏳ Comenzar FASE 1.2: Mejorar extracción de SVG

### Corto plazo (Próximas 2 semanas)
- Completar FASE 1: Estabilización
- Completar FASE 2: Testing
- Comenzar FASE 3: Optimización

### Mediano plazo (Próximo mes)
- Completar FASE 3: Optimización
- Completar FASE 4: Mejoras de Calidad
- Release v0.2.0

### Largo plazo (Próximos 3 meses)
- FASE 5: Funcionalidades Adicionales
- FASE 6: Documentación y Pulido
- Release v1.0.0

---

## 📝 Notas

### Decisiones de Diseño
- **PyTorch opcional**: Reduce tamaño pero mantiene funcionalidad avanzada
- **Caché local**: Simple y efectivo, sin dependencias externas
- **Tests con mocks**: Evita costos de API en CI

### Riesgos Identificados
- ⚠️ Renderizado SVG puede ser complejo en diferentes OS
- ⚠️ APIs de LLMs pueden cambiar
- ⚠️ Costos de API pueden ser altos con muchos tests

### Dependencias Externas
- GTK3 Runtime (Windows)
- API keys de proveedores
- Node.js (si usamos SVGO)

---

## 🔄 Actualización del Documento

Este documento debe actualizarse:
- ✅ Al completar cada tarea (cambiar estado)
- ✅ Al encontrar nuevos problemas
- ✅ Al cambiar prioridades
- ✅ Semanalmente (revisión de progreso)

**Última actualización**: Febrero 2025  
**Próxima revisión**: Pendiente de inicio
