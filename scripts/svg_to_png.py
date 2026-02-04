import argparse
import os
from pathlib import Path

# Agregar GTK3 al PATH para Cairo
gtk_path = r"C:\Program Files\GTK3-Runtime Win64\bin"
if gtk_path not in os.environ['PATH']:
    os.environ['PATH'] = gtk_path + os.pathsep + os.environ['PATH']

import cairosvg

def convert_svg_to_png(svg_path: str, png_path: str):
    """Convierte un archivo SVG a PNG"""
    try:
        svg2png(url=svg_path, write_to=png_path)
        print(f"Archivo generado: {png_path}")
    except Exception as e:
        print(f"Error al convertir el archivo: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convierte SVG a PNG')
    parser.add_argument('svg_path', help='Ruta al archivo SVG de entrada')
    parser.add_argument('png_path', help='Ruta al archivo PNG de salida')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.svg_path):
        raise FileNotFoundError(f"El archivo SVG {args.svg_path} no existe")
    
    os.makedirs(os.path.dirname(args.png_path), exist_ok=True)
    convert_svg_to_png(args.svg_path, args.png_path)
