"""Script para ejecutar la suite de pruebas y comparar resultados."""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vectorizer import Vectorizer


class TestSuiteRunner:
    """Ejecutor de suite de pruebas con comparación de resultados."""
    
    def __init__(self, suite_dir: str = "test_suite", api_key: str = None, provider: str = "anthropic"):
        """Inicializa el runner.
        
        Args:
            suite_dir: Directorio de la suite de pruebas.
            api_key: API key del proveedor.
            provider: Proveedor a usar.
        """
        self.suite_dir = Path(suite_dir)
        self.reference_dir = self.suite_dir / "reference_svg"
        self.input_dir = self.suite_dir / "input_png"
        self.output_dir = self.suite_dir / "output_svg"
        
        if not api_key:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("API key no configurada")
        
        self.vectorizer = Vectorizer(
            api_key=api_key,
            provider=provider,
            max_iterations=10,
            quality_threshold=0.85,
            verbose=True,
        )
        
        self.results = []
    
    def run_test(self, test_name: str) -> Dict:
        """Ejecuta un test individual.
        
        Args:
            test_name: Nombre del test (sin extensión).
        
        Returns:
            Diccionario con resultados.
        """
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"{'='*60}")
        
        # Rutas
        input_png = self.input_dir / f"{test_name}.png"
        output_svg = self.output_dir / f"{test_name}.svg"
        reference_svg = self.reference_dir / f"{test_name}.svg"
        
        if not input_png.exists():
            print(f"✗ PNG no encontrado: {input_png}")
            return {'success': False, 'error': 'PNG not found'}
        
        if not reference_svg.exists():
            print(f"✗ SVG de referencia no encontrado: {reference_svg}")
            return {'success': False, 'error': 'Reference SVG not found'}
        
        # Leer SVG de referencia
        reference_code = reference_svg.read_text(encoding='utf-8')
        
        print(f"Input PNG: {input_png}")
        print(f"Output SVG: {output_svg}")
        print(f"Reference SVG: {reference_svg}")
        
        # Ejecutar vectorización
        start_time = time.time()
        
        try:
            result = self.vectorizer.vectorize(
                input_path=str(input_png),
                output_path=str(output_svg),
            )
            
            elapsed = time.time() - start_time
            
            # Leer SVG generado
            generated_code = output_svg.read_text(encoding='utf-8')
            
            # Comparar con referencia
            comparison = self._compare_svgs(reference_code, generated_code)
            
            test_result = {
                'success': True,
                'test_name': test_name,
                'quality': result.quality,
                'iterations': result.iterations,
                'elapsed_time': elapsed,
                'metrics': result.metrics,
                'comparison': comparison,
                'reference_svg': str(reference_svg),
                'generated_svg': str(output_svg),
            }
            
            self._print_result(test_result)
            
        except Exception as e:
            elapsed = time.time() - start_time
            test_result = {
                'success': False,
                'test_name': test_name,
                'error': str(e),
                'elapsed_time': elapsed,
            }
            
            print(f"✗ ERROR: {e}")
        
        return test_result
    
    def _compare_svgs(self, reference: str, generated: str) -> Dict:
        """Compara SVG de referencia con generado.
        
        Args:
            reference: Código SVG de referencia.
            generated: Código SVG generado.
        
        Returns:
            Diccionario con comparación.
        """
        import re
        
        # Extraer elementos de ambos SVGs
        ref_analysis = self._analyze_svg(reference)
        gen_analysis = self._analyze_svg(generated)
        
        # Comparar
        comparison = {
            'reference': ref_analysis,
            'generated': gen_analysis,
            'matches': {},
            'differences': [],
        }
        
        # Comparar elementos
        for key in ['text_elements', 'circle_elements', 'rect_elements', 'polygon_elements']:
            ref_val = ref_analysis[key]
            gen_val = gen_analysis[key]
            comparison['matches'][key] = (ref_val == gen_val)
            if ref_val != gen_val:
                comparison['differences'].append(f"{key}: expected {ref_val}, got {gen_val}")
        
        # Comparar colores
        ref_colors = set(ref_analysis['colors'])
        gen_colors = set(gen_analysis['colors'])
        
        missing_colors = ref_colors - gen_colors
        extra_colors = gen_colors - ref_colors
        
        if missing_colors:
            comparison['differences'].append(f"Missing colors: {missing_colors}")
        if extra_colors:
            comparison['differences'].append(f"Extra colors: {extra_colors}")
        
        comparison['matches']['colors'] = (ref_colors == gen_colors)
        
        # Score de similitud (0-1)
        total_checks = len(comparison['matches'])
        matches = sum(1 for v in comparison['matches'].values() if v)
        comparison['similarity_score'] = matches / total_checks if total_checks > 0 else 0
        
        return comparison
    
    def _analyze_svg(self, svg_code: str) -> Dict:
        """Analiza un SVG.
        
        Args:
            svg_code: Código SVG.
        
        Returns:
            Diccionario con análisis.
        """
        import re
        
        # Contar elementos
        text_elements = len(re.findall(r'<text[^>]*>', svg_code))
        circle_elements = len(re.findall(r'<circle[^>]*>', svg_code))
        rect_elements = len(re.findall(r'<rect[^>]*>', svg_code))
        polygon_elements = len(re.findall(r'<polygon[^>]*>', svg_code))
        path_elements = len(re.findall(r'<path[^>]*>', svg_code))
        
        # Extraer colores
        colors = set()
        colors.update(re.findall(r'fill="(#[0-9A-Fa-f]{6})"', svg_code))
        colors.update(re.findall(r'stroke="(#[0-9A-Fa-f]{6})"', svg_code))
        
        # Extraer texto
        texts = re.findall(r'<text[^>]*>(.*?)</text>', svg_code)
        
        return {
            'text_elements': text_elements,
            'circle_elements': circle_elements,
            'rect_elements': rect_elements,
            'polygon_elements': polygon_elements,
            'path_elements': path_elements,
            'total_elements': text_elements + circle_elements + rect_elements + polygon_elements + path_elements,
            'colors': list(colors),
            'texts': texts,
            'has_viewbox': 'viewBox' in svg_code,
        }
    
    def _print_result(self, result: Dict):
        """Imprime resultado.
        
        Args:
            result: Diccionario con resultado.
        """
        print(f"\n{'='*60}")
        print(f"RESULTADO: {result['test_name']}")
        print(f"{'='*60}")
        print(f"✓ Calidad: {result['quality']:.4f}")
        print(f"✓ Iteraciones: {result['iterations']}")
        print(f"✓ Tiempo: {result['elapsed_time']:.2f}s")
        
        if 'metrics' in result:
            if 'ssim' in result['metrics']:
                print(f"✓ SSIM: {result['metrics']['ssim']:.4f}")
        
        # Comparación
        comp = result['comparison']
        print(f"\nComparación con referencia:")
        print(f"  Similitud: {comp['similarity_score']:.2%}")
        
        print(f"\n  Referencia:")
        ref = comp['reference']
        print(f"    - Texto: {ref['text_elements']}")
        print(f"    - Círculos: {ref['circle_elements']}")
        print(f"    - Rectángulos: {ref['rect_elements']}")
        print(f"    - Polígonos: {ref['polygon_elements']}")
        print(f"    - Colores: {len(ref['colors'])} {ref['colors']}")
        
        print(f"\n  Generado:")
        gen = comp['generated']
        print(f"    - Texto: {gen['text_elements']} {'✓' if comp['matches']['text_elements'] else '✗'}")
        print(f"    - Círculos: {gen['circle_elements']} {'✓' if comp['matches']['circle_elements'] else '✗'}")
        print(f"    - Rectángulos: {gen['rect_elements']} {'✓' if comp['matches']['rect_elements'] else '✗'}")
        print(f"    - Polígonos: {gen['polygon_elements']} {'✓' if comp['matches']['polygon_elements'] else '✗'}")
        print(f"    - Colores: {len(gen['colors'])} {gen['colors']} {'✓' if comp['matches']['colors'] else '✗'}")
        
        if comp['differences']:
            print(f"\n  Diferencias:")
            for diff in comp['differences']:
                print(f"    - {diff}")
        
        print(f"{'='*60}\n")
    
    def run_all(self, pattern: str = "*.png"):
        """Ejecuta todos los tests.
        
        Args:
            pattern: Patrón de archivos a procesar.
        """
        print(f"\n{'#'*60}")
        print("EJECUTANDO SUITE DE PRUEBAS")
        print(f"{'#'*60}\n")
        
        # Encontrar todos los PNGs
        png_files = sorted(self.input_dir.glob(pattern))
        
        if not png_files:
            print(f"✗ No se encontraron archivos PNG en {self.input_dir}")
            return
        
        print(f"Tests encontrados: {len(png_files)}")
        
        # Ejecutar cada test
        for png_file in png_files:
            test_name = png_file.stem
            result = self.run_test(test_name)
            self.results.append(result)
        
        # Generar reporte
        self.generate_report()
    
    def generate_report(self):
        """Genera reporte de resultados."""
        successful = [r for r in self.results if r.get('success')]
        failed = [r for r in self.results if not r.get('success')]
        
        # Calcular estadísticas
        if successful:
            avg_quality = sum(r['quality'] for r in successful) / len(successful)
            avg_iterations = sum(r['iterations'] for r in successful) / len(successful)
            avg_time = sum(r['elapsed_time'] for r in successful) / len(successful)
            avg_similarity = sum(r['comparison']['similarity_score'] for r in successful) / len(successful)
        else:
            avg_quality = avg_iterations = avg_time = avg_similarity = 0
        
        # Agrupar por dificultad
        by_difficulty = {'easy': [], 'medium': [], 'hard': []}
        for r in successful:
            name = r['test_name']
            if 'easy' in name:
                by_difficulty['easy'].append(r)
            elif 'medium' in name:
                by_difficulty['medium'].append(r)
            elif 'hard' in name:
                by_difficulty['hard'].append(r)
        
        report = {
            'summary': {
                'total': len(self.results),
                'successful': len(successful),
                'failed': len(failed),
                'avg_quality': avg_quality,
                'avg_iterations': avg_iterations,
                'avg_time': avg_time,
                'avg_similarity': avg_similarity,
            },
            'by_difficulty': {},
            'results': self.results,
        }
        
        # Estadísticas por dificultad
        for diff, results in by_difficulty.items():
            if results:
                report['by_difficulty'][diff] = {
                    'count': len(results),
                    'avg_quality': sum(r['quality'] for r in results) / len(results),
                    'avg_iterations': sum(r['iterations'] for r in results) / len(results),
                    'avg_similarity': sum(r['comparison']['similarity_score'] for r in results) / len(results),
                }
        
        # Guardar reporte
        report_file = self.suite_dir / "test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Imprimir resumen
        print(f"\n{'#'*60}")
        print("REPORTE DE RESULTADOS")
        print(f"{'#'*60}")
        print(f"\nTotal de tests: {report['summary']['total']}")
        print(f"Exitosos: {report['summary']['successful']}")
        print(f"Fallidos: {report['summary']['failed']}")
        
        if successful:
            print(f"\nPromedios generales:")
            print(f"  - Calidad: {report['summary']['avg_quality']:.4f}")
            print(f"  - Similitud con referencia: {report['summary']['avg_similarity']:.2%}")
            print(f"  - Iteraciones: {report['summary']['avg_iterations']:.1f}")
            print(f"  - Tiempo: {report['summary']['avg_time']:.2f}s")
            
            print(f"\nPor dificultad:")
            for diff, stats in report['by_difficulty'].items():
                if stats:
                    print(f"  {diff.upper()}:")
                    print(f"    - Tests: {stats['count']}")
                    print(f"    - Calidad: {stats['avg_quality']:.4f}")
                    print(f"    - Similitud: {stats['avg_similarity']:.2%}")
                    print(f"    - Iteraciones: {stats['avg_iterations']:.1f}")
        
        print(f"\nReporte guardado en: {report_file}")
        print(f"{'#'*60}\n")


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ejecutar suite de pruebas")
    parser.add_argument("--suite-dir", default="test_suite", help="Directorio de la suite")
    parser.add_argument("--provider", default="anthropic", help="Proveedor de API")
    parser.add_argument("--pattern", default="*.png", help="Patrón de archivos")
    
    args = parser.parse_args()
    
    runner = TestSuiteRunner(suite_dir=args.suite_dir, provider=args.provider)
    runner.run_all(pattern=args.pattern)


if __name__ == "__main__":
    main()
