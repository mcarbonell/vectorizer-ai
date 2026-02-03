"""Prototipo: Refinamiento visual con 2 imágenes + SVG."""
import os
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import asyncio

load_dotenv()

# Agregar GTK3 al PATH
gtk_path = r"C:\Program Files\GTK3-Runtime Win64\bin"
if gtk_path not in os.environ['PATH']:
    os.environ['PATH'] = gtk_path + os.pathsep + os.environ['PATH']

async def visual_refinement_prompt(
    original_image_path: Path,
    rendered_image_path: Path,
    current_svg: str,
    model: str = "gemini-2.5-flash"
) -> str:
    """Genera modificaciones usando análisis visual de 2 imágenes.
    
    Args:
        original_image_path: Imagen objetivo (la que queremos recrear)
        rendered_image_path: Imagen generada por el SVG actual
        current_svg: Código SVG actual
        model: Modelo de Gemini a usar
    
    Returns:
        SVG modificado
    """
    import google.generativeai as genai
    
    # Configurar API
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    
    # Cargar imágenes
    original_img = Image.open(original_image_path)
    rendered_img = Image.open(rendered_image_path)
    
    # Crear prompt
    prompt = f"""Eres un experto en SVG. Tu tarea es modificar un código SVG para que se parezca lo más posible a una imagen objetivo.

CONTEXTO:
- Imagen A (primera imagen): Es la imagen OBJETIVO que debes recrear EXACTAMENTE
- Imagen B (segunda imagen): Es el resultado actual del SVG que generaste
- SVG actual (código abajo): Es el código que generó la Imagen B

TAREA:
Analiza las diferencias entre la Imagen A (objetivo) y la Imagen B (actual) y modifica el SVG para que la Imagen B se parezca EXACTAMENTE a la Imagen A.

ANÁLISIS CRÍTICO:
1. ¿Qué elementos están en B pero NO deberían estar (elementos extra)?
2. ¿Qué elementos faltan en B que SÍ están en A?
3. ¿Los colores son exactamente iguales?
4. ¿Las posiciones y tamaños son correctos?
5. ¿El texto es del tamaño correcto?

REGLAS IMPORTANTES:
1. Si la Imagen A tiene fondo blanco limpio, NO agregues rectángulos negros
2. Si ves bandas o elementos en B que NO están en A, ELIMÍNALOS
3. El viewBox debe coincidir con las proporciones de la imagen A
4. El texto debe ser legible y del tamaño apropiado
5. Usa SOLO los elementos necesarios para recrear A
6. NO inventes elementos que no están en A

SVG ACTUAL:
{current_svg}

RESPONDE SOLO CON EL SVG MODIFICADO, sin explicaciones:"""

    # Llamar a Gemini con 2 imágenes
    model_instance = genai.GenerativeModel(model)
    
    response = model_instance.generate_content([
        prompt,
        original_img,  # Imagen A (objetivo)
        rendered_img,  # Imagen B (actual)
    ])
    
    # Extraer SVG de la respuesta
    svg_code = response.text.strip()
    
    # Limpiar markdown si existe
    if "```svg" in svg_code:
        svg_code = svg_code.split("```svg")[1].split("```")[0].strip()
    elif "```" in svg_code:
        svg_code = svg_code.split("```")[1].split("```")[0].strip()
    
    return svg_code


async def test_visual_refinement():
    """Prueba el refinamiento visual con el texto HELLO."""
    
    # Paths - usar el texto que tiene problemas
    original = Path("test_suite/input_png/easy_04_text_hello.png")
    
    # Leer SVG actual (el que tiene bandas negras)
    svg_path = Path("test_suite/output_svg/easy_04_text_hello.svg")
    with open(svg_path, 'r', encoding='utf-8') as f:
        current_svg = f.read()
    
    # Renderizar SVG actual para tener la "Imagen B"
    from src.vectorizer.comparator import ImageComparator
    comparator = ImageComparator()
    
    rendered = Path("temp/iteration_test.png")
    comparator.render_svg(current_svg, str(rendered), width=300, height=300)
    
    print(f"\n{'='*60}")
    print(f"TEST: Refinamiento Visual con 2 Imágenes")
    print(f"{'='*60}\n")
    print(f"Imagen A (objetivo): {original}")
    print(f"Imagen B (actual): {rendered}")
    print(f"\nSVG actual:")
    print(current_svg)
    print(f"\n{'='*60}")
    print(f"Llamando a Gemini con 2 imágenes...")
    print(f"{'='*60}\n")
    
    # Llamar a Gemini
    modified_svg = await visual_refinement_prompt(
        original,
        rendered,
        current_svg
    )
    
    print(f"SVG modificado:")
    print(modified_svg)
    
    # Guardar resultado
    output_path = Path("test_suite/output_svg/easy_04_visual_refined.svg")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(modified_svg)
    
    print(f"\n{'='*60}")
    print(f"SVG guardado en: {output_path}")
    print(f"{'='*60}")
    
    # Ahora renderizar y comparar
    # Renderizar SVG modificado
    refined_png = Path("temp/visual_refined.png")
    comparator.render_svg(modified_svg, str(refined_png), width=300, height=300)
    
    # Comparar con original
    comparison = comparator.compare(str(original), str(refined_png))
    
    print(f"\nCalidad después del refinamiento visual: {comparison.quality_score:.4f}")
    print(f"Diferencias encontradas: {len(comparison.differences)}")


if __name__ == "__main__":
    asyncio.run(test_visual_refinement())
