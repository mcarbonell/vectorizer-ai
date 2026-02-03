"""Script para generar suite de pruebas SVG→PNG→SVG."""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vectorizer.comparator import ImageComparator


class TestSuiteGenerator:
    """Generador de suite de pruebas con SVGs de referencia."""
    
    def __init__(self, output_dir: str = "test_suite"):
        """Inicializa el generador.
        
        Args:
            output_dir: Directorio de salida.
        """
        self.output_dir = Path(output_dir)
        self.svg_dir = self.output_dir / "reference_svg"
        self.png_dir = self.output_dir / "input_png"
        self.result_dir = self.output_dir / "output_svg"
        
        # Crear directorios
        self.svg_dir.mkdir(parents=True, exist_ok=True)
        self.png_dir.mkdir(parents=True, exist_ok=True)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        
        self.comparator = ImageComparator()
    
    def create_test_case(self, name: str, svg_code: str, difficulty: str, description: str):
        """Crea un caso de prueba.
        
        Args:
            name: Nombre del test (sin extensión).
            svg_code: Código SVG de referencia.
            difficulty: Nivel de dificultad (easy, medium, hard).
            description: Descripción del test.
        """
        print(f"\n{'='*60}")
        print(f"Creando: {name}")
        print(f"Dificultad: {difficulty.upper()}")
        print(f"Descripción: {description}")
        print(f"{'='*60}")
        
        # Guardar SVG de referencia
        svg_path = self.svg_dir / f"{name}.svg"
        svg_path.write_text(svg_code, encoding='utf-8')
        print(f"✓ SVG guardado: {svg_path}")
        
        # Renderizar SVG a PNG
        png_path = self.png_dir / f"{name}.png"
        try:
            self.comparator.render_svg(svg_code, str(png_path), width=512, height=512)
            print(f"✓ PNG generado: {png_path}")
        except Exception as e:
            print(f"✗ Error generando PNG: {e}")
            return False
        
        # Crear archivo de metadata
        meta_path = self.output_dir / f"{name}.meta.txt"
        meta_content = f"""Test Case: {name}
Difficulty: {difficulty}
Description: {description}

Files:
- Reference SVG: reference_svg/{name}.svg
- Input PNG: input_png/{name}.png
- Output SVG: output_svg/{name}.svg (generado por vectorizador)

Expected:
- El SVG generado debe ser similar al SVG de referencia
- Verificar: colores, formas, texto, proporciones
"""
        meta_path.write_text(meta_content, encoding='utf-8')
        print(f"✓ Metadata guardada: {meta_path}")
        
        return True
    
    def generate_easy_tests(self):
        """Genera tests de nivel FÁCIL."""
        print(f"\n{'#'*60}")
        print("GENERANDO TESTS NIVEL FÁCIL")
        print(f"{'#'*60}")
        
        # Test 1: Círculo rojo simple
        self.create_test_case(
            name="easy_01_red_circle",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#FF0000"/>
</svg>''',
            difficulty="easy",
            description="Círculo rojo centrado, color sólido"
        )
        
        # Test 2: Cuadrado azul
        self.create_test_case(
            name="easy_02_blue_square",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect x="20" y="20" width="60" height="60" fill="#0066CC"/>
</svg>''',
            difficulty="easy",
            description="Cuadrado azul centrado"
        )
        
        # Test 3: Triángulo verde
        self.create_test_case(
            name="easy_03_green_triangle",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <polygon points="50,20 80,80 20,80" fill="#00CC66"/>
</svg>''',
            difficulty="easy",
            description="Triángulo verde equilátero"
        )
        
        # Test 4: Texto simple
        self.create_test_case(
            name="easy_04_text_hello",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">
  <text x="100" y="55" text-anchor="middle" font-family="Arial" font-size="32" fill="#000000">HELLO</text>
</svg>''',
            difficulty="easy",
            description="Texto 'HELLO' en negro, centrado"
        )
        
        # Test 5: Dos círculos
        self.create_test_case(
            name="easy_05_two_circles",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 100">
  <circle cx="40" cy="50" r="30" fill="#FF0000"/>
  <circle cx="110" cy="50" r="30" fill="#0000FF"/>
</svg>''',
            difficulty="easy",
            description="Dos círculos: rojo y azul"
        )
    
    def generate_medium_tests(self):
        """Genera tests de nivel MEDIO."""
        print(f"\n{'#'*60}")
        print("GENERANDO TESTS NIVEL MEDIO")
        print(f"{'#'*60}")
        
        # Test 1: Logo simple con texto y forma
        self.create_test_case(
            name="medium_01_logo_text_shape",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">
  <rect x="10" y="10" width="180" height="80" rx="10" fill="#F0F0F0"/>
  <circle cx="50" cy="50" r="25" fill="#FF6600"/>
  <text x="100" y="55" font-family="Arial" font-size="24" font-weight="bold" fill="#333333">LOGO</text>
</svg>''',
            difficulty="medium",
            description="Logo con círculo naranja y texto 'LOGO'"
        )
        
        # Test 2: Icono con múltiples formas
        self.create_test_case(
            name="medium_02_icon_star",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="45" fill="#FFD700"/>
  <polygon points="50,20 61,43 85,43 66,58 73,80 50,65 27,80 34,58 15,43 39,43" fill="#FFFFFF"/>
</svg>''',
            difficulty="medium",
            description="Estrella blanca sobre círculo dorado"
        )
        
        # Test 3: Badge con texto
        self.create_test_case(
            name="medium_03_badge",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 40">
  <rect width="120" height="40" rx="20" fill="#4CAF50"/>
  <text x="60" y="25" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold" fill="#FFFFFF">SUCCESS</text>
</svg>''',
            difficulty="medium",
            description="Badge verde con texto 'SUCCESS'"
        )
        
        # Test 4: Logo con dos colores de texto
        self.create_test_case(
            name="medium_04_two_color_text",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 80">
  <text x="10" y="50" font-family="Arial" font-size="36" font-weight="bold" fill="#0066CC">Quali</text>
  <text x="100" y="50" font-family="Arial" font-size="36" font-weight="bold" fill="#00CC66">dades</text>
</svg>''',
            difficulty="medium",
            description="Texto 'Qualidades' con dos colores"
        )
        
        # Test 5: Icono con formas superpuestas
        self.create_test_case(
            name="medium_05_overlapping",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 100">
  <rect x="20" y="30" width="50" height="50" fill="#FF6B6B"/>
  <circle cx="70" cy="50" r="30" fill="#4ECDC4"/>
</svg>''',
            difficulty="medium",
            description="Rectángulo rojo y círculo turquesa superpuestos"
        )
    
    def generate_hard_tests(self):
        """Genera tests de nivel DIFÍCIL."""
        print(f"\n{'#'*60}")
        print("GENERANDO TESTS NIVEL DIFÍCIL")
        print(f"{'#'*60}")
        
        # Test 1: Logo complejo
        self.create_test_case(
            name="hard_01_complex_logo",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">
  <rect width="200" height="100" fill="#FFFFFF"/>
  <circle cx="50" cy="50" r="35" fill="#FF6B6B"/>
  <rect x="40" y="40" width="20" height="20" fill="#FFFFFF"/>
  <text x="100" y="45" font-family="Arial" font-size="28" font-weight="bold" fill="#2C3E50">Brand</text>
  <text x="100" y="70" font-family="Arial" font-size="14" fill="#7F8C8D">tagline here</text>
</svg>''',
            difficulty="hard",
            description="Logo con círculo, rectángulo y dos textos"
        )
        
        # Test 2: Múltiples elementos
        self.create_test_case(
            name="hard_02_multiple_elements",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 150">
  <rect x="10" y="10" width="180" height="130" rx="15" fill="#F8F9FA"/>
  <circle cx="50" cy="50" r="25" fill="#FF6B6B"/>
  <rect x="90" y="25" width="50" height="50" fill="#4ECDC4"/>
  <polygon points="170,30 190,70 150,70" fill="#FFD93D"/>
  <text x="100" y="120" text-anchor="middle" font-family="Arial" font-size="20" fill="#2C3E50">Shapes</text>
</svg>''',
            difficulty="hard",
            description="Múltiples formas con texto"
        )
        
        # Test 3: Texto con múltiples líneas
        self.create_test_case(
            name="hard_03_multiline_text",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 120">
  <text x="100" y="40" text-anchor="middle" font-family="Arial" font-size="24" font-weight="bold" fill="#2C3E50">Title</text>
  <text x="100" y="70" text-anchor="middle" font-family="Arial" font-size="16" fill="#7F8C8D">Subtitle here</text>
  <text x="100" y="95" text-anchor="middle" font-family="Arial" font-size="12" fill="#95A5A6">Small text</text>
</svg>''',
            difficulty="hard",
            description="Tres líneas de texto con diferentes tamaños"
        )
        
        # Test 4: Patrón de formas
        self.create_test_case(
            name="hard_04_pattern",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 150">
  <circle cx="40" cy="40" r="20" fill="#FF6B6B"/>
  <circle cx="110" cy="40" r="20" fill="#4ECDC4"/>
  <circle cx="40" cy="110" r="20" fill="#FFD93D"/>
  <circle cx="110" cy="110" r="20" fill="#95E1D3"/>
  <circle cx="75" cy="75" r="25" fill="#2C3E50"/>
</svg>''',
            difficulty="hard",
            description="Patrón de 5 círculos de colores"
        )
        
        # Test 5: Logo con sombra simulada
        self.create_test_case(
            name="hard_05_shadow_effect",
            svg_code='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 150">
  <ellipse cx="77" cy="77" rx="45" ry="45" fill="#CCCCCC" opacity="0.3"/>
  <circle cx="75" cy="75" r="45" fill="#FF6B6B"/>
  <text x="75" y="85" text-anchor="middle" font-family="Arial" font-size="32" font-weight="bold" fill="#FFFFFF">A</text>
</svg>''',
            difficulty="hard",
            description="Círculo con efecto de sombra y letra"
        )
    
    def generate_all(self):
        """Genera toda la suite de pruebas."""
        print(f"\n{'='*60}")
        print("GENERADOR DE SUITE DE PRUEBAS SVG→PNG→SVG")
        print(f"{'='*60}")
        print(f"Directorio de salida: {self.output_dir}")
        print(f"{'='*60}\n")
        
        self.generate_easy_tests()
        self.generate_medium_tests()
        self.generate_hard_tests()
        
        print(f"\n{'='*60}")
        print("SUITE DE PRUEBAS GENERADA")
        print(f"{'='*60}")
        print(f"\nArchivos creados en: {self.output_dir}/")
        print(f"  - reference_svg/  : SVGs de referencia (ground truth)")
        print(f"  - input_png/      : PNGs para vectorizar")
        print(f"  - output_svg/     : SVGs generados (vacío inicialmente)")
        print(f"  - *.meta.txt      : Metadata de cada test")
        
        print(f"\nPróximos pasos:")
        print(f"  1. Revisar SVGs de referencia en reference_svg/")
        print(f"  2. Verificar PNGs generados en input_png/")
        print(f"  3. Ejecutar vectorizador:")
        print(f"     python scripts/run_test_suite.py")
        print(f"  4. Comparar output_svg/ con reference_svg/")
        print(f"{'='*60}\n")


def main():
    """Función principal."""
    generator = TestSuiteGenerator(output_dir="test_suite")
    generator.generate_all()


if __name__ == "__main__":
    main()
