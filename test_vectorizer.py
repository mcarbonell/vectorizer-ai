"""Script simple para probar el vectorizador y analizar resultados."""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar GTK3 al PATH
gtk_path = r"C:\Program Files\GTK3-Runtime Win64\bin"
if gtk_path not in os.environ['PATH']:
    os.environ['PATH'] = gtk_path + os.pathsep + os.environ['PATH']

# Ejecutar vectorizador
from src.vectorizer.core import Vectorizer
from pathlib import Path

async def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    
    vectorizer = Vectorizer(
        provider="google",
        model="gemini-2.5-flash",
        api_key=api_key,
        max_iterations=3,  # Solo 3 iteraciones para probar
        quality_threshold=0.85
    )
    
    input_path = Path("test_suite/input_png/qualidades.png")
    output_path = Path("test_suite/output_svg/qualidades.svg")
    
    print(f"Vectorizando: {input_path}")
    result = await vectorizer.vectorize_async(input_path, output_path)
    
    print(f"\n{'='*60}")
    print(f"RESULTADO:")
    print(f"{'='*60}")
    print(f"Calidad final: {result.quality:.4f}")
    print(f"Iteraciones: {result.iterations}")
    print(f"Métricas: {result.metrics}")
    print(f"SVG guardado en: {output_path}")
    print(f"\nPrimeras líneas del SVG:")
    print(result.svg_code[:500])

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
