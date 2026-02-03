# Descubrimientos de la Sesión - 2026-02-03

## Problema Identificado: Proporciones en Renderizado

### El Problema Original
Al generar PNGs desde SVGs de referencia, estábamos usando dimensiones fijas (300x300) sin respetar las proporciones del viewBox original.

**Ejemplo**:
- SVG: `viewBox="0 0 200 100"` (proporción 2:1, rectangular)
- PNG generado: 300x300 (cuadrado)
- Resultado: Áreas transparentes arriba/abajo

### Consecuencias

1. **Transparencia → Negro**
   - Cairo renderiza el SVG centrado en el cuadrado
   - Las áreas no cubiertas quedan transparentes (canal alpha)
   - Gemini interpreta la transparencia como negro
   - Genera rectángulos negros en el SVG

2. **Calidad Reducida**
   - El SVG generado incluye elementos que no están en el original
   - Las métricas de comparación penalizan estos elementos extra
   - Calidad baja (61.9% → 37.46% después de corrección)

### La Solución

Modificar `generate_pngs_from_svgs.py` para:
1. Extraer el viewBox del SVG
2. Calcular proporciones (aspect ratio)
3. Generar PNG con dimensiones proporcionales
4. Usar RGB en lugar de RGBA (sin canal alpha)

**Código**:
```python
# Extraer viewBox
viewbox_match = re.search(r'viewBox="([^"]+)"', svg_content)
x, y, vb_width, vb_height = map(float, viewbox.split())

# Calcular dimensiones manteniendo proporción
aspect_ratio = vb_width / vb_height

if aspect_ratio >= 1:  # Más ancho que alto
    width = max_size
    height = int(max_size / aspect_ratio)
else:  # Más alto que ancho
    height = max_size
    width = int(max_size * aspect_ratio)
```

**Resultados**:
- Antes: 300x300 RGBA (con transparencia)
- Después: 300x150 RGB (sin transparencia)
- ✅ Sin bandas negras
- ⚠️ Calidad aún baja por otros factores

---

## Enfoque de Refinamiento: 2 Imágenes + SVG

### La Idea
En lugar de analizar diferencias por cuadrantes, pasar al LLM:
1. **Imagen A**: Objetivo (PNG original)
2. **Imagen B**: Resultado actual (SVG renderizado)
3. **SVG actual**: Código a modificar

**Prompt**:
```
Analiza las diferencias entre la Imagen A (objetivo) y la Imagen B (actual)
y modifica el SVG para que B se parezca lo más posible a A.
```

### Pruebas Realizadas

#### Test 1: Círculo Rojo (easy_01)
- **Calidad inicial**: 99.95%
- **Resultado**: Gemini devolvió el mismo SVG (ya era perfecto)
- **Conclusión**: ✅ Funciona, pero no hay nada que mejorar

#### Test 2: Texto HELLO (easy_04) - Con bandas negras
- **Calidad inicial**: 61.9%
- **Problema**: Imagen A también tenía bandas negras (artefacto de renderizado)
- **Resultado**: Gemini ajustó las bandas (empeoró a 52.45%)
- **Conclusión**: ❌ El modelo reproduce fielmente lo que ve, incluyendo artefactos

#### Test 3: Texto HELLO (easy_04) - Sin bandas negras
- **Calidad inicial**: 37.46%
- **Resultado**: Ajustó font-size de 40 a 25 (mejoró a 39.11%)
- **Conclusión**: ⚠️ Mejora marginal, diferencias demasiado sutiles

### Ventajas del Enfoque

✅ **Más intuitivo**: El modelo "ve" las diferencias
✅ **Menos código**: No necesita análisis por cuadrantes
✅ **Más flexible**: Funciona con cualquier tipo de imagen
✅ **Contexto visual**: El modelo entiende la tarea globalmente

### Limitaciones Identificadas

❌ **Diferencias sutiles**: Font-size 32 vs 40 es difícil de ver
❌ **Posiciones exactas**: x="100" vs x="50%" es difícil de distinguir visualmente
❌ **Elementos innecesarios**: No detecta que el fondo blanco sobra
❌ **Dependencia de calidad de renderizado**: Si el PNG tiene artefactos, los reproduce

### Mejoras Necesarias

1. **Prompt más específico**
   - Indicar qué buscar (tamaño de texto, posición, colores exactos)
   - Dar ejemplos de diferencias comunes
   - Enfatizar eliminación de elementos extra

2. **Análisis híbrido**
   - Usar visión para diferencias globales
   - Usar parsing de SVG para diferencias precisas
   - Combinar ambos enfoques

3. **Información adicional**
   - Incluir análisis original de la imagen A
   - Especificar colores esperados (hex)
   - Indicar dimensiones del viewBox

---

## Comparación de Enfoques

### Enfoque Actual (Cuadrantes)
```python
# Divide imagen en cuadrantes
# Analiza diferencias por región
# Genera modificaciones vagas
modifications = [
    "Ajustar colores en el area center",
    "Mejorar precision de formas en top-left"
]
```

**Pros**:
- Estructurado
- Predecible

**Contras**:
- Modificaciones vagas
- No ve la imagen completa
- Difícil de ajustar

### Enfoque Propuesto (2 Imágenes)
```python
# Pasa 2 imágenes + SVG al LLM
response = model.generate_content([
    prompt,
    imagen_objetivo,
    imagen_actual
])
```

**Pros**:
- Más intuitivo
- Contexto visual completo
- Flexible

**Contras**:
- Diferencias sutiles difíciles de detectar
- Depende de calidad de renderizado
- Menos control sobre qué modificar

### Enfoque Híbrido (Recomendado)
```python
# 1. Análisis visual (2 imágenes)
visual_diff = analyze_visual_differences(img_a, img_b)

# 2. Análisis estructural (parsing SVG)
structural_diff = compare_svg_elements(svg_actual, svg_referencia)

# 3. Combinar
modifications = merge_analyses(visual_diff, structural_diff)
# "El texto está en x=50% pero debería estar en x=100"
# "El font-size es 40 pero debería ser 32"
# "Hay un rect de fondo que no debería estar"
```

---

## Métricas de Calidad

### Problema con SSIM
SSIM (Structural Similarity Index) es sensible a:
- Diferencias de tamaño/escala
- Diferencias de posición
- Diferencias sutiles de color

**Ejemplo**:
- Font-size 32 vs 40: Gran diferencia en SSIM
- Posición x=100 vs x=105: Diferencia moderada en SSIM
- Color #000000 vs #000001: Diferencia mínima en SSIM

### CLIP Similarity
CLIP es más robusto para:
- Similitud semántica
- Contenido general
- Composición

Pero menos preciso para:
- Detalles exactos
- Colores específicos
- Posiciones precisas

### Recomendación
Usar **múltiples métricas**:
1. **SSIM**: Para similitud estructural
2. **CLIP**: Para similitud semántica
3. **Comparación de elementos**: Para precisión exacta

---

## Próximos Pasos

### 🔴 Inmediato
1. ✅ **Arreglar proporciones en renderizado** - COMPLETADO
2. ⏳ **Re-ejecutar tests fáciles** con PNGs corregidos
3. ⏳ **Documentar mejoras** en calidad

### 🟡 Corto Plazo
4. **Implementar enfoque híbrido**
   - Análisis visual (2 imágenes)
   - Análisis estructural (parsing SVG)
   - Combinar ambos

5. **Mejorar prompts**
   - Más específicos
   - Con ejemplos
   - Con análisis original

6. **Comparador de SVG**
   - Parsear elementos
   - Comparar atributos
   - Generar diferencias precisas

### 🟢 Medio Plazo
7. **Tests medios y difíciles**
8. **Optimización de prompts**
9. **Documentación de patrones**

---

## Lecciones Aprendidas

### 1. Proporciones Importan
No asumir dimensiones fijas. Siempre respetar el aspect ratio del contenido original.

### 2. Transparencia es Problemática
En contextos de IA visual, la transparencia puede interpretarse de formas inesperadas. Mejor usar fondos sólidos.

### 3. Visión vs Precisión
Los modelos de visión son excelentes para entender contenido general, pero luchan con diferencias sutiles (font-size, posiciones exactas).

### 4. Contexto es Clave
Pasar más contexto al LLM (análisis original, colores esperados, dimensiones) mejora significativamente los resultados.

### 5. Iteración Ciega
El enfoque actual de modificación es "ciego" - el LLM no ve las imágenes, solo recibe instrucciones textuales. Esto limita su efectividad.

---

## Código de Ejemplo: Enfoque Híbrido

```python
async def hybrid_refinement(
    original_image: Path,
    current_svg: str,
    reference_svg: str = None
) -> str:
    """Refinamiento híbrido: visual + estructural."""
    
    # 1. Renderizar SVG actual
    rendered_image = render_svg(current_svg)
    
    # 2. Análisis visual (2 imágenes)
    visual_prompt = f"""
    Compara estas dos imágenes:
    - Imagen A: Objetivo
    - Imagen B: Actual
    
    Lista las diferencias principales:
    """
    
    visual_analysis = await gemini.analyze([
        visual_prompt,
        original_image,
        rendered_image
    ])
    
    # 3. Análisis estructural (si hay referencia)
    structural_diffs = []
    if reference_svg:
        ref_elements = parse_svg(reference_svg)
        cur_elements = parse_svg(current_svg)
        structural_diffs = compare_elements(ref_elements, cur_elements)
    
    # 4. Combinar análisis
    modifications = []
    
    # De análisis visual
    modifications.extend(visual_analysis.differences)
    
    # De análisis estructural (más precisos)
    for diff in structural_diffs:
        if diff.type == "text":
            modifications.append(
                f"Cambiar texto en {diff.element_id}: "
                f"font-size de {diff.current} a {diff.expected}"
            )
        elif diff.type == "position":
            modifications.append(
                f"Mover {diff.element_type} de "
                f"({diff.current_x}, {diff.current_y}) a "
                f"({diff.expected_x}, {diff.expected_y})"
            )
    
    # 5. Generar SVG modificado
    modification_prompt = f"""
    Modifica este SVG aplicando estos cambios ESPECÍFICOS:
    
    {chr(10).join(f"- {mod}" for mod in modifications)}
    
    SVG ACTUAL:
    {current_svg}
    
    SVG MODIFICADO:
    """
    
    modified_svg = await gemini.generate(modification_prompt)
    
    return modified_svg
```

---

**Última actualización**: 2026-02-03 23:50
