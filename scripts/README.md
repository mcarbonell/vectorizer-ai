# 🛠️ Scripts de Utilidad

Scripts para facilitar el desarrollo, gestión y pruebas de calidad del proyecto.

---

## 📊 Gestión de Progreso

### `progress.py`
Script para gestionar el progreso del proyecto.

```bash
# Ver estado actual
python scripts/progress.py status

# Listar tareas pendientes
python scripts/progress.py list

# Listar tareas de una fase específica
python scripts/progress.py list FASE_1

# Marcar tarea como completada
python scripts/progress.py complete 1.1

# Agregar entrada al log
python scripts/progress.py log "Implementado feature X"
```

---

## 🧪 Suite de Pruebas de Calidad

### Metodología SVG→PNG→SVG

Creamos SVGs de referencia, los rasterizamos a PNG, y luego vectorizamos el PNG para comparar con el SVG original.

**Ventajas**:
- Control total sobre qué debe generar
- Ground truth para comparación precisa
- Progresión controlada de dificultad
- Reproducible y automatizado

### `generate_test_suite.py`
Genera suite completa de pruebas con SVGs de referencia.

```bash
# Generar suite completa (15 tests)
python scripts/generate_test_suite.py
```

**Genera**:
- `test_suite/reference_svg/` - SVGs de referencia (ground truth)
- `test_suite/input_png/` - PNGs rasterizados (input)
- `test_suite/output_svg/` - Directorio para SVGs generados
- `test_suite/*.meta.txt` - Metadata de cada test

**Tests incluidos**:
- 5 tests fáciles (formas simples, colores sólidos)
- 5 tests medios (logos, iconos, combinaciones)
- 5 tests difíciles (múltiples elementos, efectos)

### `run_test_suite.py`
Ejecuta la suite de pruebas y genera reporte con comparaciones.

```bash
# Ejecutar todos los tests
python scripts/run_test_suite.py

# Solo tests fáciles
python scripts/run_test_suite.py --pattern "easy_*.png"

# Solo tests medios
python scripts/run_test_suite.py --pattern "medium_*.png"

# Solo tests difíciles
python scripts/run_test_suite.py --pattern "hard_*.png"

# Con proveedor específico
python scripts/run_test_suite.py --provider google
```

**Genera**:
- SVGs en `test_suite/output_svg/`
- `test_suite/test_report.json` - Reporte completo con:
  - Métricas de vectorización (calidad, iteraciones, tiempo)
  - Comparación con referencia (similitud, elementos, colores)
  - Estadísticas por dificultad
  - Diferencias detalladas

### `test_quality.py`
Script original de pruebas (ahora reemplazado por la suite SVG→PNG→SVG).

```bash
python scripts/test_quality.py
```

---

## 🔄 Workflow Recomendado

### 1. Generar Suite
```bash
python scripts/generate_test_suite.py
```

### 2. Revisar SVGs de Referencia
```bash
# Abrir en navegador para verificar
start test_suite/reference_svg/easy_01_red_circle.svg
```

### 3. Ejecutar Tests Fáciles
```bash
python scripts/run_test_suite.py --pattern "easy_*.png"
```

### 4. Analizar Resultados
```bash
# Ver reporte
cat test_suite/test_report.json

# Comparar SVGs visualmente
```

### 5. Identificar Mejoras
- ¿Qué tests tienen baja similitud?
- ¿Qué tipo de errores son comunes?
- ¿Texto como paths en lugar de <text>?
- ¿Colores incorrectos?

### 6. Ajustar Prompts
```bash
# Editar prompts
code src/vectorizer/prompts.py

# Re-ejecutar
python scripts/run_test_suite.py --pattern "easy_*.png"
```

### 7. Expandir a Tests Medios
Una vez que tests fáciles tengan >90% similitud:
```bash
python scripts/run_test_suite.py --pattern "medium_*.png"
```

---

## 📈 Métricas de Éxito

### Por Nivel

| Nivel | Similitud Min | Calidad Min | Iteraciones Max |
|-------|---------------|-------------|-----------------|
| Fácil | 90% | 0.85 | 4 |
| Medio | 80% | 0.80 | 7 |
| Difícil | 70% | 0.70 | 10 |

---

## 📚 Documentación Relacionada

- `docs/CURRENT_FOCUS.md` - Enfoque actual del proyecto
- `docs/QUALITY_IMPROVEMENT.md` - Plan detallado de mejora
- `docs/PROGRESS.md` - Progreso del proyecto

---

**¡Suite de pruebas lista para usar!** 🚀
