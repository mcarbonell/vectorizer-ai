# 🛠️ Scripts de Utilidad

Scripts para facilitar el desarrollo y gestión del proyecto.

## progress.py

Script para gestionar el progreso de las tareas del proyecto.

### Uso

```bash
# Ver progreso actual
python scripts/progress.py status

# Listar todas las tareas pendientes
python scripts/progress.py list

# Listar tareas de una fase específica
python scripts/progress.py list FASE_1

# Marcar tarea como completada
python scripts/progress.py complete 1.1

# Agregar entrada al log de trabajo
python scripts/progress.py log "Completada implementación de caché"
```

### Ejemplos

```bash
# Ver estado del proyecto
$ python scripts/progress.py status

📊 Progreso del Proyecto
==================================================
Tareas completadas: 5/31
Porcentaje: 16.1%
Barra: [█░░░░░░░░░]
==================================================

# Listar tareas pendientes de FASE 1
$ python scripts/progress.py list FASE_1

📋 Tareas Pendientes
======================================================================

### FASE_1
  🔴 1.1: Arreglar renderizado SVG (2h)
  🔴 1.2: Mejorar extracción de SVG (1h)
  🔴 1.3: Arreglar Google Gemini API (1h)

# Marcar tarea completada
$ python scripts/progress.py complete 1.1
✅ Tarea 1.1 marcada como completada

# Agregar nota al log
$ python scripts/progress.py log "Implementado renderizado con Playwright"
✅ Entrada agregada al log: Implementado renderizado con Playwright
```

## Otros Scripts (Futuros)

- `test.py` - Ejecutar tests con configuración específica
- `benchmark.py` - Benchmarks de rendimiento
- `cost_calculator.py` - Calcular costos estimados de API
