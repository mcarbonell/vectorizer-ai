"""Debug: Ver qué análisis hace de la imagen con texto."""
import os
from pathlib import Path
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Agregar GTK3 al PATH
gtk_path = r"C:\Program Files\GTK3-Runtime Win64\bin"
if gtk_path not in os.environ['PATH']:
    os.environ['PATH'] = gtk_path + os.pathsep + os.environ['PATH']

from src.vectorizer.vision import VisionAnalyzer

async def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    
    analyzer = VisionAnalyzer(
        provider="google",
        model="gemini-2.5-flash",
        api_key=api_key
    )
    
    # Analizar imagen con texto
    image_path = Path("test_suite/input_png/easy_04_text_hello.png")
    
    print(f"\n{'='*60}")
    print(f"ANÁLISIS DE IMAGEN CON TEXTO")
    print(f"{'='*60}\n")
    print(f"Imagen: {image_path}\n")
    
    analysis = await analyzer.analyze(str(image_path))
    
    print(f"Descripción: {analysis.description}")
    print(f"\nFormas: {analysis.shapes}")
    print(f"Colores: {analysis.colors}")
    print(f"Composición: {analysis.composition}")
    print(f"Complejidad: {analysis.complexity}")
    print(f"Estilo: {analysis.style}")
    
    print(f"\n{'='*60}")
    print(f"ANÁLISIS COMPLETO (dict)")
    print(f"{'='*60}\n")
    print(analysis.__dict__)

if __name__ == "__main__":
    asyncio.run(main())
