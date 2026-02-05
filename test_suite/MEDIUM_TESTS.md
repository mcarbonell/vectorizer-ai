# Tests de Nivel Medio - Preparados

**Fecha de preparación**: 2026-02-04  
**Estado**: ✅ Listos para ejecutar  
**Bloqueo**: Límite de cuota API (20 requests/día alcanzado)

---

## 📋 Tests Preparados

### MEDIUM-01: Icono de Casa
**Archivo**: `medium_01_house_icon.svg`
**Complejidad**: Múltiples formas combinadas + sombreado

**Elementos**:
- Círculo de fondo (azul claro)
- Polígono (forma de casa)
- Rectángulo (puerta)
- Rectángulo (ventana)
- Líneas (cruz de ventana)
- Bordes/stroke

**Desafíos esperados**:
- Múltiples colores (#E8F4FD, #4A90E2, #8B4513, #87CEEB)
- Forma poligonal compleja
- Stroke/bordes
- Superposición de elementos

---

### MEDIUM-02: Badge con Corazón
**Archivo**: `medium_02_heart_badge.svg`
**Complejidad**: Path SVG complejo

**Elementos**:
- Círculo de fondo (rojo)
- Path (forma de corazón)
- Curvas Bézier

**Desafíos esperados**:
- Path con curvas (`d="M... C..."`)
- Forma orgánica compleja
- Precisión del corazón

---

### MEDIUM-03: Rating de Estrellas
**Archivo**: `medium_03_star_rating.svg`
**Complejidad**: Patrón repetido 5 veces

**Elementos**:
- 5 polígonos estrella
- Posicionamiento horizontal
- Color uniforme (#FFD700)

**Desafíos esperados**:
- Detección de patrón repetido
- Posicionamiento preciso
- 5 elementos idénticos

---

### MEDIUM-04: Flechas de Intercambio
**Archivo**: `medium_04_arrows_exchange.svg`
**Complejidad**: Múltiples polígonos direccionales

**Elementos**:
- 2 polígonos (flechas opuestas)
- Círculo central
- Colores diferentes (verde/naranja)

**Desafíos esperados**:
- Orientación de flechas
- Posicionamiento simétrico
- Múltiples colores

---

### MEDIUM-05: Barra de Progreso
**Archivo**: `medium_05_progress_bar.svg`
**Complejidad**: Elementos con bordes redondeados + texto

**Elementos**:
- Rectángulo fondo (gris, bordes redondeados)
- Rectángulo progreso (verde, 75%)
- Texto porcentaje ("75%")

**Desafíos esperados**:
- Bordes redondeados (rx/ry)
- Proporciones (75%)
- Texto numérico

---

## 🎯 Objetivos de Validación

### Métricas esperadas:
- **Calidad mínima**: 60-70% (menor que formas simples)
- **SSIM**: 0.60-0.75
- **Iteraciones**: 2-3 (más que nivel fácil)

### Criterios de éxito:
1. ✅ Detectar todos los elementos principales
2. ✅ Colores aproximados (±10% del original)
3. ✅ Posicionamiento razonable
4. ✅ Formas reconocibles

---

## 🚀 Instrucciones de Ejecución

Cuando la cuota esté disponible (mañana o en ~24h):

```bash
# Usar el script de test suite
python scripts/run_test_suite.py --provider google

# O ejecutar individualmente
export PATH="/c/Program Files/GTK3-Runtime Win64/bin:$PATH"

python -m vectorizer test_suite/input_png/medium_01_house_icon.png \
       test_suite/output_svg/medium_01_result.svg \
       --provider google --model gemini-2.5-flash \
       --max-iterations 3 --threshold 0.75
```

---

## 📊 Comparación con Nivel Fácil

| Aspecto | Nivel Fácil | Nivel Medio |
|---------|-------------|-------------|
| Elementos | 1-2 | 3-7 |
| Colores | 1-2 | 3-5 |
| Formas | Simples | Combinadas |
| Texto | Simple | Numérico |
| Calidad esperada | 98-99% | 60-75% |
| Iteraciones | 1 | 2-3 |

---

## 🎨 Elementos SVG Utilizados

### Nivel Medio incluye:
- ✅ `<circle>` - Círculos
- ✅ `<rect>` - Rectángulos con/sin bordes redondeados
- ✅ `<polygon>` - Polígonos (estrellas, flechas)
- ✅ `<path>` - Paths con curvas (corazón)
- ✅ `<text>` - Texto numérico
- ✅ `stroke` - Bordes
- ✅ `rx/ry` - Bordes redondeados

### Nivel Fácil vs Medio:
| Elemento | Fácil | Medio |
|----------|-------|-------|
| circle | ✅ | ✅ |
| rect | ✅ | ✅ (+ bordes) |
| polygon | ✅ | ✅ (+ complejos) |
| text | ✅ | ✅ (+ numérico) |
| path | ❌ | ✅ |
| stroke | ❌ | ✅ |
| rx/ry | ❌ | ✅ |

---

## 📝 Notas para el Análisis

### Posibles problemas esperados:
1. **Paths complejos**: El corazón puede no ser preciso
2. **Bordes redondeados**: Pueden interpretarse como rectángulos simples
3. **Patrones repetidos**: Podrían detectarse como N elementos individuales
4. **Proporciones**: La barra de progreso (75%) puede no ser exacta

### Aspectos positivos a validar:
1. **Detección de múltiples formas**: ¿Encuentra todos los elementos?
2. **Colores**: ¿Mantiene la precisión de nivel fácil?
3. **Composición**: ¿Respeta la estructura general?
4. **Texto editable**: ¿Sigue usando `<text>` y no paths?

---

**Preparado por**: AI Assistant  
**Fecha**: 2026-02-04  
**Estado**: ✅ Listos para ejecutar cuando haya cuota disponible
