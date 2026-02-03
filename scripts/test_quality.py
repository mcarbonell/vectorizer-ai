"""Script para probar y analizar la calidad de vectorización con diferentes imágenes."""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vectorizer import Vectorizer


class QualityTester:
    """Tester para evaluar calidad de vectorización."""
    
    def __init__(self, api_key: str, provider: str = "anthropic"):
        """Inicializa el tester.
        
        Args:
            api_key: API key del proveedor.
            provider: Proveedor a usar.
        """
        self.vectorizer = Vectorizer(
            api_key=api_key,
            provider=provider,
            max_iterations=10,
            quality_threshold=0.85,
            verbose=True,
        )
        self.results = []
    
    def test_image(
        self,
        input_path: str,
        output_path: str,
        difficulty: str,
        description: str,
    ) -> Dict:
        """Prueba vectorización de una imagen.
        
        Args:
            input_path: Ruta de la imagen de entrada.
            output_path: Ruta del SVG de salida.
            difficulty: Nivel de dificultad (easy, medium, hard).
            description: Descripción de la imagen.
        
        Returns:
            Diccionario con resultados.
        """
        print(f"\n{'='*60}")
        print(f"Probando: {description}")
        print(f"Dificultad: {difficulty.upper()}")
        print(f"Input: {input_path}")
        print(f"Output: {output_path}")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        try:
            result = self.vectorizer.vectorize(
                input_path=input_path,
                output_path=output_path,
            )
            
            elapsed = time.time() - start_time
            
            # Leer SVG generado
            with open(output_path, 'r', encoding='utf-8') as f:
                svg_code = f.read()
            
            svg_size = len(svg_code)
            
            # Analizar SVG
            analysis = self._analyze_svg(svg_code)
            
            test_result = {
                'success': True,
                'description': description,
                'difficulty': difficulty,
                'input': input_path,
                'output': output_path,
                'quality': result.quality,
                'iterations': result.iterations,
                'elapsed_time': elapsed,
                'svg_size': svg_size,
                'metrics': result.metrics,
                'svg_analysis': analysis,
            }
            
            self._print_result(test_result)
            
        except Exception as e:
            elapsed = time.time() - start_time
            test_result = {
                'success': False,
                'description': description,
                'difficulty': difficulty,
                'input': input_path,
                'error': str(e),
                'elapsed_time': elapsed,
            }
            
            print(f"❌ ERROR: {e}\n")
        
        self.results.append(test_result)
        return test_result
    
    def _analyze_svg(self, svg_code: str) -> Dict:
        """Analiza el SVG generado.
        
        Args:
            svg_code: Código SVG.
        
        Returns:
            Diccionario con análisis.
        """
        import re
        
        # Contar elementos
        text_elements = len(re.findall(r'<text[^>]*>', svg_code))
        path_elements = len(re.findall(r'<path[^>]*>', svg_code))
        rect_elements = len(re.findall(r'<rect[^>]*>', svg_code))
        circle_elements = len(re.findall(r'<circle[^>]*>', svg_code))
        polygon_elements = len(re.findall(r'<polygon[^>]*>', svg_code))
        
        # Extraer colores
        colors = set(re.findall(r'fill="(#[0-9A-Fa-f]{6})"', svg_code))
        colors.update(re.findall(r'stroke="(#[0-9A-Fa-f]{6})"', svg_code))
        
        # Verificar si tiene texto editable
        has_editable_text = text_elements > 0
        
        # Verificar si tiene viewBox
        has_viewbox = 'viewBox' in svg_code
        
        return {
            'text_elements': text_elements,
            'path_elements': path_elements,
            'rect_elements': rect_elements,
            'circle_elements': circle_elements,
            'polygon_elements': polygon_elements,
            'total_elements': text_elements + path_elements + rect_elements + circle_elements + polygon_elements,
            'unique_colors': len(colors),
            'colors': list(colors),
            'has_editable_text': has_editable_text,
            'has_viewbox': has_viewbox,
        }
    
    def _print_result(self, result: Dict):
        """Imprime resultado de forma legible.
        
        Args:
            result: Diccionario con resultado.
        """
        print(f"\n{'='*60}")
        print(f"RESULTADO: {result['description']}")
        print(f"{'='*60}")
        print(f"✓ Calidad: {result['quality']:.4f}")
        print(f"✓ Iteraciones: {result['iterations']}")
        print(f"✓ Tiempo: {result['elapsed_time']:.2f}s")
        print(f"✓ Tamaño SVG: {result['svg_size']} bytes")
        
        if 'metrics' in result:
            if 'ssim' in result['metrics']:
                print(f"✓ SSIM: {result['metrics']['ssim']:.4f}")
            if 'clip_similarity' in result['metrics']:
                print(f"✓ CLIP: {result['metrics']['clip_similarity']:.4f}")
        
        analysis = result['svg_analysis']
        print(f"\nAnálisis del SVG:")
        print(f"  - Elementos totales: {analysis['total_elements']}")
        print(f"  - Texto editable: {'✓' if analysis['has_editable_text'] else '✗'} ({analysis['text_elements']} elementos)")
        print(f"  - Paths: {analysis['path_elements']}")
        print(f"  - Rectángulos: {analysis['rect_elements']}")
        print(f"  - Círculos: {analysis['circle_elements']}")
        print(f"  - Polígonos: {analysis['polygon_elements']}")
        print(f"  - Colores únicos: {analysis['unique_colors']}")
        print(f"  - ViewBox: {'✓' if analysis['has_viewbox'] else '✗'}")
        
        if analysis['colors']:
            print(f"  - Colores: {', '.join(analysis['colors'][:5])}")
        
        print(f"{'='*60}\n")
    
    def generate_report(self, output_file: str = "quality_report.json"):
        """Genera reporte de calidad.
        
        Args:
            output_file: Archivo de salida.
        """
        # Calcular estadísticas
        successful = [r for r in self.results if r.get('success')]
        failed = [r for r in self.results if not r.get('success')]
        
        if successful:
            avg_quality = sum(r['quality'] for r in successful) / len(successful)
            avg_iterations = sum(r['iterations'] for r in successful) / len(successful)
            avg_time = sum(r['elapsed_time'] for r in successful) / len(successful)
            avg_size = sum(r['svg_size'] for r in successful) / len(successful)
        else:
            avg_quality = avg_iterations = avg_time = avg_size = 0
        
        # Agrupar por dificultad
        by_difficulty = {}
        for r in successful:
            diff = r['difficulty']
            if diff not in by_difficulty:
                by_difficulty[diff] = []
            by_difficulty[diff].append(r)
        
        report = {
            'summary': {
                'total': len(self.results),
                'successful': len(successful),
                'failed': len(failed),
                'avg_quality': avg_quality,
                'avg_iterations': avg_iterations,
                'avg_time': avg_time,
                'avg_svg_size': avg_size,
            },
            'by_difficulty': {},
            'results': self.results,
        }
        
        # Estadísticas por dificultad
        for diff, results in by_difficulty.items():
            report['by_difficulty'][diff] = {
                'count': len(results),
                'avg_quality': sum(r['quality'] for r in results) / len(results),
                'avg_iterations': sum(r['iterations'] for r in results) / len(results),
                'avg_time': sum(r['elapsed_time'] for r in results) / len(results),
            }
        
        # Guardar reporte
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"REPORTE DE CALIDAD")
        print(f"{'='*60}")
        print(f"Total de pruebas: {report['summary']['total']}")
        print(f"Exitosas: {report['summary']['successful']}")
        print(f"Fallidas: {report['summary']['failed']}")
        
        if successful:
            print(f"\nPromedios:")
            print(f"  - Calidad: {report['summary']['avg_quality']:.4f}")
            print(f"  - Iteraciones: {report['summary']['avg_iterations']:.1f}")
            print(f"  - Tiempo: {report['summary']['avg_time']:.2f}s")
            print(f"  - Tamaño SVG: {report['summary']['avg_svg_size']:.0f} bytes")
            
            print(f"\nPor dificultad:")
            for diff, stats in report['by_difficulty'].items():
                print(f"  {diff.upper()}:")
                print(f"    - Pruebas: {stats['count']}")
                print(f"    - Calidad: {stats['avg_quality']:.4f}")
                print(f"    - Iteraciones: {stats['avg_iterations']:.1f}")
        
        print(f"\nReporte guardado en: {output_file}")
        print(f"{'='*60}\n")


def main():
    """Función principal."""
    # Obtener API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY no configurada")
        return
    
    # Crear tester
    tester = QualityTester(api_key=api_key, provider="anthropic")
    
    # Crear directorios
    test_images_dir = Path("test_images")
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Definir casos de prueba
    test_cases = [
        # FÁCIL: Formas simples y colores sólidos
        {
            'input': test_images_dir / 'easy_circle.png',
            'output': output_dir / 'easy_circle.svg',
            'difficulty': 'easy',
            'description': 'Círculo rojo simple',
        },
        {
            'input': test_images_dir / 'easy_square.png',
            'output': output_dir / 'easy_square.svg',
            'difficulty': 'easy',
            'description': 'Cuadrado azul simple',
        },
        {
            'input': test_images_dir / 'easy_text.png',
            'output': output_dir / 'easy_text.svg',
            'difficulty': 'easy',
            'description': 'Texto simple "HELLO"',
        },
        
        # MEDIO: Combinaciones de formas y texto
        {
            'input': test_images_dir / 'medium_logo.png',
            'output': output_dir / 'medium_logo.svg',
            'difficulty': 'medium',
            'description': 'Logo con texto y forma',
        },
        {
            'input': test_images_dir / 'medium_icon.png',
            'output': output_dir / 'medium_icon.svg',
            'difficulty': 'medium',
            'description': 'Icono con múltiples colores',
        },
        
        # DIFÍCIL: Formas complejas, gradientes, sombras
        {
            'input': test_images_dir / 'hard_gradient.png',
            'output': output_dir / 'hard_gradient.svg',
            'difficulty': 'hard',
            'description': 'Forma con gradiente',
        },
        {
            'input': test_images_dir / 'hard_detailed.png',
            'output': output_dir / 'hard_detailed.svg',
            'difficulty': 'hard',
            'description': 'Logo detallado con sombras',
        },
    ]
    
    # Ejecutar pruebas solo para imágenes que existen
    print(f"\n{'='*60}")
    print(f"INICIANDO PRUEBAS DE CALIDAD")
    print(f"{'='*60}\n")
    
    for test_case in test_cases:
        if Path(test_case['input']).exists():
            tester.test_image(
                input_path=str(test_case['input']),
                output_path=str(test_case['output']),
                difficulty=test_case['difficulty'],
                description=test_case['description'],
            )
        else:
            print(f"⚠️  Imagen no encontrada: {test_case['input']}")
            print(f"   Saltando: {test_case['description']}\n")
    
    # Generar reporte
    if tester.results:
        tester.generate_report(output_file=str(output_dir / "quality_report.json"))
    else:
        print("\n⚠️  No se ejecutaron pruebas. Crea imágenes de prueba en test_images/")
        print("\nEjemplos de imágenes a crear:")
        for test_case in test_cases:
            print(f"  - {test_case['input']}: {test_case['description']}")


if __name__ == "__main__":
    main()
