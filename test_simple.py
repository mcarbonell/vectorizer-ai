"""Prueba simple con el círculo rojo."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar GTK3 al PATH
gtk_path = r"C:\Program Files\GTK3-Runtime Win64\bin"
if gtk_path not in os.environ['PATH']:
    os.environ['PATH'] = gtk_path + os.pathsep + os.environ['PATH']

from src.vectorizer.core import Vectorizer

async def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    
    vectorizer = Vectorizer(
        provider="google",
        model="gemini-2.5-flash",
        api_key=api_key,
        max_iterations=3,
        quality_threshold=0.85
    )
    
    # Test más simple: texto HELLO
    input_path = Path("test_suite/input_png/easy_04_text_hello.png")
    output_path = Path("test_suite/output_svg/easy_04_text_hello.svg")
    
    print(f"\n{'='*60}")
    print(f"TEST: Texto HELLO (easy_04)")
    print(f"{'='*60}\n")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}\n")
    
    result = await vectorizer.vectorize_async(input_path, output_path)
    
    print(f"\n{'='*60}")
    print(f"RESULTADO")
    print(f"{'='*60}")
    print(f"Calidad: {result.quality:.4f}")
    print(f"Iteraciones: {result.iterations}")
    print(f"Métricas: {result.metrics}")
    print(f"\nSVG generado:")
    print(result.svg_code)
    
    # Comparar con referencia
    reference_path = Path("test_suite/reference_svg/easy_04_text_hello.svg")
    with open(reference_path, 'r', encoding='utf-8') as f:
        reference_svg = f.read()
    
    print(f"\n{'='*60}")
    print(f"SVG DE REFERENCIA")
    print(f"{'='*60}")
    print(reference_svg)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
