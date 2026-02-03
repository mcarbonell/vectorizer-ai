"""Ejemplo de uso del modo batch de Vectorizer AI."""

import os
from pathlib import Path
from vectorizer import Vectorizer

# Configurar API key
api_key = os.environ.get("ANTHROPIC_API_KEY")

# Crear instancia del vectorizador
vectorizer = Vectorizer(
    api_key=api_key,
    model="claude-3-5-sonnet-20241022",
    max_iterations=5,  # Menos iteraciones para batch
    quality_threshold=0.80,
    verbose=True,
    provider="anthropic",
)


def example_1_list_of_files():
    """Ejemplo 1: Procesar lista específica de archivos."""
    print("\n" + "=" * 60)
    print("EJEMPLO 1: Lista de archivos")
    print("=" * 60)
    
    input_files = [
        "images/logo1.png",
        "images/logo2.png",
        "images/icon1.png",
    ]
    
    output_dir = "./output/batch1"
    
    # Callback para mostrar progreso
    def progress(filename, current, total, quality):
        print(f"[{current}/{total}] {filename} - Calidad: {quality:.4f}")
    
    result = vectorizer.vectorize_batch(
        input_paths=input_files,
        output_dir=output_dir,
        callback=progress,
        continue_on_error=True,
    )
    
    print(f"\n✓ Completado: {result.successful}/{result.total}")
    print(f"✗ Fallidos: {result.failed}")
    print(f"⏱ Tiempo: {result.metadata['elapsed_time']:.2f}s")
    
    if result.results:
        avg_quality = sum(r['quality'] for r in result.results) / len(result.results)
        print(f"📊 Calidad promedio: {avg_quality:.4f}")


def example_2_glob_pattern():
    """Ejemplo 2: Procesar archivos con patrón glob."""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Patrón glob")
    print("=" * 60)
    
    # Procesar todos los PNG en un directorio
    pattern = "images/*.png"
    output_dir = "./output/batch2"
    
    result = vectorizer.vectorize_batch(
        input_paths=pattern,
        output_dir=output_dir,
        continue_on_error=True,
    )
    
    print(f"\n✓ Completado: {result.successful}/{result.total}")
    print(f"✗ Fallidos: {result.failed}")
    
    # Mostrar resultados individuales
    print("\nResultados:")
    for r in result.results:
        print(f"  {r['filename']}: {r['quality']:.4f} ({r['iterations']} iter)")


def example_3_parallel():
    """Ejemplo 3: Procesamiento paralelo (experimental)."""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Procesamiento paralelo")
    print("=" * 60)
    
    pattern = "images/*.png"
    output_dir = "./output/batch3"
    
    result = vectorizer.vectorize_batch(
        input_paths=pattern,
        output_dir=output_dir,
        parallel=True,
        max_workers=3,  # 3 imágenes en paralelo
        continue_on_error=True,
    )
    
    print(f"\n✓ Completado: {result.successful}/{result.total}")
    print(f"⏱ Tiempo: {result.metadata['elapsed_time']:.2f}s")
    print(f"⚡ Workers: {result.metadata['max_workers']}")


def example_4_error_handling():
    """Ejemplo 4: Manejo de errores."""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Manejo de errores")
    print("=" * 60)
    
    input_files = [
        "images/valid.png",
        "images/invalid.txt",  # Archivo inválido
        "images/missing.png",  # Archivo que no existe
        "images/valid2.png",
    ]
    
    output_dir = "./output/batch4"
    
    result = vectorizer.vectorize_batch(
        input_paths=input_files,
        output_dir=output_dir,
        continue_on_error=True,  # Continuar a pesar de errores
    )
    
    print(f"\n✓ Exitosos: {result.successful}")
    print(f"✗ Fallidos: {result.failed}")
    
    if result.errors:
        print("\nErrores:")
        for error in result.errors:
            print(f"  {error['filename']}: {error['error']}")


def example_5_recursive():
    """Ejemplo 5: Procesar recursivamente subdirectorios."""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: Búsqueda recursiva")
    print("=" * 60)
    
    # Procesar todos los PNG en subdirectorios
    pattern = "images/**/*.png"
    output_dir = "./output/batch5"
    
    result = vectorizer.vectorize_batch(
        input_paths=pattern,
        output_dir=output_dir,
        continue_on_error=True,
    )
    
    print(f"\n✓ Completado: {result.successful}/{result.total}")
    print(f"📁 Output: {output_dir}")


if __name__ == "__main__":
    # Ejecutar ejemplos
    print("🎨 Vectorizer AI - Ejemplos de Modo Batch")
    
    # Descomentar el ejemplo que quieras ejecutar:
    
    # example_1_list_of_files()
    # example_2_glob_pattern()
    # example_3_parallel()
    # example_4_error_handling()
    # example_5_recursive()
    
    print("\n✨ Ejemplos completados!")
