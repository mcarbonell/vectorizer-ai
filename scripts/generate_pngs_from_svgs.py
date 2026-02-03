"""Genera PNGs desde los SVGs de referencia para testing."""
import os
import sys
from pathlib import Path

# Agregar GTK3 al PATH para Cairo
gtk_path = r"C:\Program Files\GTK3-Runtime Win64\bin"
if gtk_path not in os.environ['PATH']:
    os.environ['PATH'] = gtk_path + os.pathsep + os.environ['PATH']

try:
    import cairosvg
    print("✓ Cairo disponible")
except ImportError as e:
    print(f"✗ Error importando Cairo: {e}")
    print("\nInstala cairosvg: pip install cairosvg")
    print("En Windows también necesitas GTK3: winget install tschoonj.GTKForWindows")
    sys.exit(1)

def generate_png_from_svg(svg_path: Path, png_path: Path, max_size: int = 300):
    """Genera un PNG desde un SVG usando cairosvg.
    
    Args:
        svg_path: Ruta al archivo SVG
        png_path: Ruta donde guardar el PNG
        max_size: Tamaño máximo (el lado más largo será este tamaño)
    """
    try:
        # Leer SVG
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        # Extraer viewBox para calcular proporciones
        import re
        viewbox_match = re.search(r'viewBox="([^"]+)"', svg_content)
        
        if viewbox_match:
            viewbox = viewbox_match.group(1)
            parts = viewbox.split()
            if len(parts) == 4:
                x, y, vb_width, vb_height = map(float, parts)
                
                # Calcular dimensiones manteniendo proporción
                aspect_ratio = vb_width / vb_height
                
                if aspect_ratio >= 1:  # Más ancho que alto
                    width = max_size
                    height = int(max_size / aspect_ratio)
                else:  # Más alto que ancho
                    height = max_size
                    width = int(max_size * aspect_ratio)
            else:
                # Fallback a cuadrado
                width = height = max_size
        else:
            # Sin viewBox, usar cuadrado
            width = height = max_size
        
        # Agregar fondo blanco si el SVG no tiene uno
        if '<rect' not in svg_content or 'fill="white"' not in svg_content.lower():
            # Insertar rectángulo blanco después del tag <svg>
            svg_lines = svg_content.split('\n')
            for i, line in enumerate(svg_lines):
                if '<svg' in line and '>' in line:
                    if viewbox_match:
                        viewbox = viewbox_match.group(1)
                        parts = viewbox.split()
                        if len(parts) == 4:
                            x, y, w, h = parts
                            svg_lines.insert(i + 1, f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white"/>')
                            break
            svg_content = '\n'.join(svg_lines)
        
        # Convertir a PNG con dimensiones correctas
        cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            write_to=str(png_path),
            output_width=width,
            output_height=height
        )
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Genera todos los PNGs desde los SVGs de referencia."""
    # Directorios
    reference_dir = Path("test_suite/reference_svg")
    output_dir = Path("test_suite/input_png")
    
    # Crear directorio de salida si no existe
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Obtener todos los SVGs
    svg_files = sorted(reference_dir.glob("*.svg"))
    
    if not svg_files:
        print(f"✗ No se encontraron archivos SVG en {reference_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"Generando PNGs desde SVGs de referencia")
    print(f"{'='*60}\n")
    print(f"SVGs encontrados: {len(svg_files)}")
    print(f"Directorio de salida: {output_dir}\n")
    
    # Contadores
    success_count = 0
    error_count = 0
    
    # Procesar cada SVG
    for svg_path in svg_files:
        # Nombre del PNG (mismo nombre que SVG)
        png_name = svg_path.stem + ".png"
        png_path = output_dir / png_name
        
        print(f"Procesando: {svg_path.name}")
        print(f"  → {png_name}")
        
        # Generar PNG
        if generate_png_from_svg(svg_path, png_path):
            print(f"  ✓ Generado correctamente")
            success_count += 1
        else:
            error_count += 1
        
        print()
    
    # Resumen
    print(f"{'='*60}")
    print(f"RESUMEN")
    print(f"{'='*60}")
    print(f"✓ Exitosos: {success_count}")
    print(f"✗ Errores: {error_count}")
    print(f"Total: {len(svg_files)}")
    print(f"\nPNGs guardados en: {output_dir.absolute()}")

if __name__ == "__main__":
    main()
