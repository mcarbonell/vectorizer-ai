"""Prueba todos los tests fáciles."""
import os
from pathlib import Path
from dotenv import load_dotenv
import asyncio

# Cargar variables de entorno
load_dotenv()

# Agregar GTK3 al PATH
gtk_path = r"C:\Program Files\GTK3-Runtime Win64\bin"
if gtk_path not in os.environ['PATH']:
    os.environ['PATH'] = gtk_path + os.pathsep + os.environ['PATH']

from src.vectorizer.core import Vectorizer

async def test_image(vectorizer, test_name, input_path, output_path, reference_path):
    """Prueba una imagen y compara con referencia."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}\n")
    
    result = await vectorizer.vectorize_async(input_path, output_path)
    
    # Leer referencia
    with open(reference_path, 'r', encoding='utf-8') as f:
        reference_svg = f.read().strip()
    
    print(f"Calidad: {result.quality:.4f}")
    print(f"Iteraciones: {result.iterations}")
    print(f"SSIM: {result.metrics.get('ssim', 0):.4f}")
    print(f"CLIP: {result.metrics.get('clip_similarity', 0):.4f}")
    
    # Comparación simple
    generated_svg = result.svg_code.strip()
    
    print(f"\nSVG Generado ({len(generated_svg)} chars):")
    print(generated_svg[:200] + "..." if len(generated_svg) > 200 else generated_svg)
    
    print(f"\nSVG Referencia ({len(reference_svg)} chars):")
    print(reference_svg[:200] + "..." if len(reference_svg) > 200 else reference_svg)
    
    return {
        'test': test_name,
        'quality': result.quality,
        'iterations': result.iterations,
        'ssim': result.metrics.get('ssim', 0),
        'clip': result.metrics.get('clip_similarity', 0),
    }

async def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    
    vectorizer = Vectorizer(
        provider="google",
        model="gemini-2.5-flash",
        api_key=api_key,
        max_iterations=5,
        quality_threshold=0.85
    )
    
    # Tests fáciles
    tests = [
        ("Círculo Rojo", "easy_01_red_circle"),
        ("Cuadrado Azul", "easy_02_blue_square"),
        ("Triángulo Verde", "easy_03_green_triangle"),
        ("Texto HELLO", "easy_04_text_hello"),
        ("Dos Círculos", "easy_05_two_circles"),
    ]
    
    results = []
    
    for test_name, file_name in tests:
        input_path = Path(f"test_suite/input_png/{file_name}.png")
        output_path = Path(f"test_suite/output_svg/{file_name}.svg")
        reference_path = Path(f"test_suite/reference_svg/{file_name}.svg")
        
        result = await test_image(vectorizer, test_name, input_path, output_path, reference_path)
        results.append(result)
        
        # Pequeña pausa entre tests
        await asyncio.sleep(1)
    
    # Resumen
    print(f"\n{'='*60}")
    print(f"RESUMEN - TESTS FÁCILES")
    print(f"{'='*60}\n")
    
    for r in results:
        status = "✓" if r['quality'] >= 0.85 else "✗"
        print(f"{status} {r['test']:20s} | Calidad: {r['quality']:.4f} | Iter: {r['iterations']} | SSIM: {r['ssim']:.4f}")
    
    # Estadísticas
    avg_quality = sum(r['quality'] for r in results) / len(results)
    avg_iterations = sum(r['iterations'] for r in results) / len(results)
    success_rate = sum(1 for r in results if r['quality'] >= 0.85) / len(results) * 100
    
    print(f"\n{'='*60}")
    print(f"ESTADÍSTICAS")
    print(f"{'='*60}")
    print(f"Calidad promedio: {avg_quality:.4f}")
    print(f"Iteraciones promedio: {avg_iterations:.1f}")
    print(f"Tasa de éxito (>0.85): {success_rate:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())
