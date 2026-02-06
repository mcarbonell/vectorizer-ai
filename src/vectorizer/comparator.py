"""Módulo de comparación de imágenes para Vectorizer AI."""

import logging
from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image

from .models import ComparisonResult

logger = logging.getLogger(__name__)


class ImageComparator:
    """Compara imágenes y calcula métricas de similitud."""

    def __init__(self) -> None:
        """Inicializa el ImageComparator."""
        pass

    def compare(self, image1_path: str, image2_path: str) -> ComparisonResult:
        """Compara dos imágenes usando múltiples métricas.

        Args:
            image1_path: Ruta a la primera imagen.
            image2_path: Ruta a la segunda imagen.

        Returns:
            ComparisonResult con el resultado de la comparación.
        """
        logger.info(f"Comparando: {image1_path} vs {image2_path}")

        # Cargar imágenes
        img1 = self._load_image(image1_path)
        img2 = self._load_image(image2_path)

        # Redimensionar al mismo tamaño
        img1, img2 = self._resize_to_match(img1, img2)

        # Calcular SSIM
        ssim = self._calculate_ssim(img1, img2)

        # Calcular similitud de píxeles
        pixel_similarity = self._calculate_pixel_similarity(img1, img2)

        # Identificar diferencias
        differences = self._find_differences(img1, img2)

        # Calcular puntuación de calidad
        quality_score = self._calculate_quality_score(ssim, pixel_similarity)

        return ComparisonResult(
            ssim=ssim,
            clip_similarity=pixel_similarity,
            quality_score=quality_score,
            differences=differences,
            metadata={
                "image1_path": str(Path(image1_path)),
                "image2_path": str(Path(image2_path)),
            },
        )

    def render_svg(
        self,
        svg_code: str,
        output_path: str,
        width: int = 1024,
        height: int = 1024,
        source_image_path: str = None,
    ) -> None:
        """Renderiza un SVG a PNG.

        Args:
            svg_code: Código SVG a renderizar.
            output_path: Ruta donde guardar el PNG.
            width: Ancho de la imagen.
            height: Alto de la imagen.
            source_image_path: Ruta de la imagen original para usar sus dimensiones.

        Raises:
            RuntimeError: Si no hay método de renderizado disponible.
        """
        # Si se proporciona la imagen fuente, usar sus dimensiones
        if source_image_path and Path(source_image_path).exists():
            try:
                with Image.open(source_image_path) as img:
                    width, height = img.size
                    logger.info(
                        f"Usando dimensiones de imagen original: {width}x{height}"
                    )
            except Exception as e:
                logger.warning(
                    f"No se pudieron obtener dimensiones de la imagen fuente: {e}"
                )
        logger.info(f"Renderizando SVG a: {output_path}")

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        errors = []

        # Método 1: cairosvg (más confiable)
        try:
            import cairosvg

            cairosvg.svg2png(
                bytestring=svg_code.encode("utf-8"),
                write_to=output_path,
                output_width=width,
                output_height=height,
            )
            logger.info("SVG renderizado con cairosvg")
            return
        except ImportError:
            errors.append("cairosvg no instalado")
        except Exception as e:
            errors.append(f"cairosvg falló: {e}")
            logger.debug(f"cairosvg error: {e}")

        # Método 2: svglib + reportlab
        try:
            from reportlab.graphics import renderPM
            from svglib.svglib import svg2rlg

            temp_svg = output_file.with_suffix(".temp.svg")
            temp_svg.write_text(svg_code, encoding="utf-8")

            drawing = svg2rlg(str(temp_svg))
            if drawing:
                renderPM.drawToFile(drawing, output_path, fmt="PNG", dpi=72)
                temp_svg.unlink(missing_ok=True)
                logger.info("SVG renderizado con svglib")
                return
        except ImportError:
            errors.append("svglib/reportlab no instalado")
        except Exception as e:
            errors.append(f"svglib falló: {e}")
            logger.debug(f"svglib error: {e}")

        # Método 3: wand (ImageMagick)
        try:
            from wand.image import Image as WandImage

            with WandImage(blob=svg_code.encode("utf-8"), format="svg") as img:
                img.format = "png"
                img.resize(width, height)
                img.save(filename=output_path)
            logger.info("SVG renderizado con wand")
            return
        except ImportError:
            errors.append("wand no instalado")
        except Exception as e:
            errors.append(f"wand falló: {e}")
            logger.debug(f"wand error: {e}")

        # Método 4: Renderizado simple con Pillow (fallback para formas básicas)
        try:
            self._render_svg_with_pillow(svg_code, output_path, width, height)
            logger.info("SVG renderizado con Pillow (fallback)")
            return
        except Exception as e:
            errors.append(f"Pillow fallback falló: {e}")
            logger.debug(f"Pillow error: {e}")

        # Sin métodos disponibles
        error_msg = (
            "No se pudo renderizar el SVG. Métodos intentados:\n"
            + "\n".join(f"  - {err}" for err in errors)
            + "\n\nInstala cairosvg: pip install cairosvg\n"
            + "En Windows también necesitas GTK3: winget install tschoonj.GTKForWindows"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    def _render_svg_with_pillow(
        self,
        svg_code: str,
        output_path: str,
        width: int,
        height: int,
    ) -> None:
        """Renderiza SVG básico usando Pillow (fallback).

        Soporta: rect, circle, ellipse, polygon, text básico.

        Args:
            svg_code: Código SVG a renderizar.
            output_path: Ruta donde guardar el PNG.
            width: Ancho de la imagen.
            height: Alto de la imagen.
        """
        import re

        from PIL import ImageDraw

        # Crear imagen con fondo blanco
        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)

        # Extraer elementos del SVG con regex simple

        # Rectángulos: <rect x="10" y="10" width="100" height="100" fill="red"/>
        rects = re.findall(r"<rect[^>]*>", svg_code, re.IGNORECASE)
        for rect in rects:
            x = (
                float(re.search(r'x=["\']([^"\']+)["\']', rect).group(1))
                if re.search(r'x=["\']([^"\']+)["\']', rect)
                else 0
            )
            y = (
                float(re.search(r'y=["\']([^"\']+)["\']', rect).group(1))
                if re.search(r'y=["\']([^"\']+)["\']', rect)
                else 0
            )
            w = (
                float(re.search(r'width=["\']([^"\']+)["\']', rect).group(1))
                if re.search(r'width=["\']([^"\']+)["\']', rect)
                else 100
            )
            h = (
                float(re.search(r'height=["\']([^"\']+)["\']', rect).group(1))
                if re.search(r'height=["\']([^"\']+)["\']', rect)
                else 100
            )
            fill_match = re.search(r'fill=["\']([^"\']+)["\']', rect)
            fill = fill_match.group(1) if fill_match else "black"

            # Escalar coordenadas al tamaño de salida
            # Asumimos viewBox de 100x100 si no se especifica
            vb_match = re.search(r'viewBox=["\']([^"\']+)["\']', svg_code)
            if vb_match:
                vb = vb_match.group(1).split()
                if len(vb) == 4:
                    vb_w, vb_h = float(vb[2]), float(vb[3])
                    scale_x = width / vb_w
                    scale_y = height / vb_h
                    x, y = x * scale_x, y * scale_y
                    w, h = w * scale_x, h * scale_y

            draw.rectangle([x, y, x + w, y + h], fill=fill)

        # Círculos: <circle cx="50" cy="50" r="40" fill="red"/>
        circles = re.findall(r"<circle[^>]*>", svg_code, re.IGNORECASE)
        for circle in circles:
            cx = (
                float(re.search(r'cx=["\']([^"\']+)["\']', circle).group(1))
                if re.search(r'cx=["\']([^"\']+)["\']', circle)
                else 50
            )
            cy = (
                float(re.search(r'cy=["\']([^"\']+)["\']', circle).group(1))
                if re.search(r'cy=["\']([^"\']+)["\']', circle)
                else 50
            )
            r = (
                float(re.search(r'r=["\']([^"\']+)["\']', circle).group(1))
                if re.search(r'r=["\']([^"\']+)["\']', circle)
                else 40
            )
            fill_match = re.search(r'fill=["\']([^"\']+)["\']', circle)
            fill = fill_match.group(1) if fill_match else "black"

            # Escalar
            vb_match = re.search(r'viewBox=["\']([^"\']+)["\']', svg_code)
            if vb_match:
                vb = vb_match.group(1).split()
                if len(vb) == 4:
                    vb_w, vb_h = float(vb[2]), float(vb[3])
                    scale_x = width / vb_w
                    scale_y = height / vb_h
                    cx, cy = cx * scale_x, cy * scale_y
                    r = r * min(scale_x, scale_y)

            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)

        # Polígonos: <polygon points="x1,y1 x2,y2 x3,y3" fill="red"/>
        polygons = re.findall(r"<polygon[^>]*>", svg_code, re.IGNORECASE)
        for poly in polygons:
            points_match = re.search(r'points=["\']([^"\']+)["\']', poly)
            if points_match:
                points_str = points_match.group(1)
                points = []
                for pt in points_str.split():
                    if "," in pt:
                        x, y = map(float, pt.split(","))
                        points.append((x, y))

                # Escalar
                vb_match = re.search(r'viewBox=["\']([^"\']+)["\']', svg_code)
                if vb_match and points:
                    vb = vb_match.group(1).split()
                    if len(vb) == 4:
                        vb_w, vb_h = float(vb[2]), float(vb[3])
                        scale_x = width / vb_w
                        scale_y = height / vb_h
                        points = [(x * scale_x, y * scale_y) for x, y in points]

                fill_match = re.search(r'fill=["\']([^"\']+)["\']', poly)
                fill = fill_match.group(1) if fill_match else "black"
                if len(points) >= 3:
                    draw.polygon(points, fill=fill)

        # Texto básico: <text x="50" y="50" fill="black">Hola</text>
        texts = re.findall(r"<text[^>]*>([^<]*)</text>", svg_code, re.IGNORECASE)
        for i, text_content in enumerate(texts):
            if text_content.strip():
                # Buscar los atributos del texto actual
                text_match = re.findall(r"<text[^>]*>", svg_code, re.IGNORECASE)[i]
                x = (
                    float(re.search(r'x=["\']([^"\']+)["\']', text_match).group(1))
                    if re.search(r'x=["\']([^"\']+)["\']', text_match)
                    else 50
                )
                y = (
                    float(re.search(r'y=["\']([^"\']+)["\']', text_match).group(1))
                    if re.search(r'y=["\']([^"\']+)["\']', text_match)
                    else 50
                )
                fill_match = re.search(r'fill=["\']([^"\']+)["\']', text_match)
                fill = fill_match.group(1) if fill_match else "black"

                # Escalar
                vb_match = re.search(r'viewBox=["\']([^"\']+)["\']', svg_code)
                if vb_match:
                    vb = vb_match.group(1).split()
                    if len(vb) == 4:
                        vb_w, vb_h = float(vb[2]), float(vb[3])
                        scale_x = width / vb_w
                        scale_y = height / vb_h
                        x, y = x * scale_x, y * scale_y

                draw.text((x, y), text_content.strip(), fill=fill)

        # Guardar
        img.save(output_path, "PNG")

    def _load_image(self, image_path: str) -> np.ndarray:
        """Carga una imagen y la convierte a numpy array.

        Args:
            image_path: Ruta a la imagen.

        Returns:
            Array numpy con la imagen.
        """
        img = Image.open(image_path).convert("RGB")
        return np.array(img)

    def _resize_to_match(
        self, img1: np.ndarray, img2: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Redimensiona dos imágenes al mismo tamaño.

        Args:
            img1: Primera imagen.
            img2: Segunda imagen.

        Returns:
            Tupla con las imágenes redimensionadas.
        """
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]

        # Usar el tamaño más pequeño
        target_h = min(h1, h2)
        target_w = min(w1, w2)

        if h1 != target_h or w1 != target_w:
            img1 = self._resize_image(img1, target_w, target_h)

        if h2 != target_h or w2 != target_w:
            img2 = self._resize_image(img2, target_w, target_h)

        return img1, img2

    def _resize_image(self, img: np.ndarray, width: int, height: int) -> np.ndarray:
        """Redimensiona una imagen.

        Args:
            img: Imagen a redimensionar.
            width: Ancho deseado.
            height: Alto deseado.

        Returns:
            Imagen redimensionada.
        """
        pil_img = Image.fromarray(img)
        resized = pil_img.resize((width, height), Image.LANCZOS)
        return np.array(resized)

    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calcula el índice de similitud estructural (SSIM).

        Args:
            img1: Primera imagen.
            img2: Segunda imagen.

        Returns:
            Valor SSIM entre 0 y 1.
        """
        from skimage.metrics import structural_similarity as ssim_func

        # Convertir a escala de grises
        gray1 = np.dot(img1[..., :3], [0.2989, 0.5870, 0.1140])
        gray2 = np.dot(img2[..., :3], [0.2989, 0.5870, 0.1140])

        # Calcular SSIM con data_range correcto (255 para imágenes de 8 bits)
        # Usar 255 como data_range porque las imágenes son de 0-255
        score = ssim_func(gray1, gray2, data_range=255.0)

        # Asegurar que el resultado está entre 0 y 1
        score = max(0.0, min(1.0, float(score)))

        return score

    def _calculate_pixel_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calcula la similitud de píxeles entre dos imágenes.

        Args:
            img1: Primera imagen.
            img2: Segunda imagen.

        Returns:
            Valor de similitud entre 0 y 1.
        """
        # Convertir a float y normalizar
        img1_float = img1.astype(np.float32) / 255.0
        img2_float = img2.astype(np.float32) / 255.0

        # Calcular diferencia absoluta
        diff = np.abs(img1_float - img2_float)

        # Calcular similitud (1 - media de diferencias)
        similarity = 1.0 - np.mean(diff)

        return float(similarity)

    def _find_differences(self, img1: np.ndarray, img2: np.ndarray) -> List[dict]:
        """Identifica las diferencias entre dos imágenes.

        Args:
            img1: Primera imagen.
            img2: Segunda imagen.

        Returns:
            Lista de diferencias encontradas.
        """
        differences: List[dict] = []

        # Calcular diferencia absoluta
        diff = np.abs(img1.astype(np.int16) - img2.astype(np.int16))

        # Calcular umbral de diferencia
        threshold = 30  # Diferencia perceptible

        # Crear máscara de diferencias
        mask = np.any(diff > threshold, axis=2)

        # Si no hay diferencias significativas
        if not np.any(mask):
            return differences

        # Encontrar regiones con diferencias
        h, w = mask.shape

        # Dividir en cuadrantes para identificar áreas
        quadrants = [
            ("top_left", 0, 0, w // 2, h // 2),
            ("top_right", w // 2, 0, w, h // 2),
            ("bottom_left", 0, h // 2, w // 2, h),
            ("bottom_right", w // 2, h // 2, w, h),
            ("center", w // 4, h // 4, 3 * w // 4, 3 * h // 4),
        ]

        for name, x1, y1, x2, y2 in quadrants:
            quadrant_mask = mask[y1:y2, x1:x2]
            diff_pixels = np.sum(quadrant_mask)
            total_pixels = (y2 - y1) * (x2 - x1)
            diff_ratio = diff_pixels / total_pixels if total_pixels > 0 else 0

            if diff_ratio > 0.01:  # Más del 1% de diferencia
                quadrant_diff = diff[y1:y2, x1:x2]
                avg_diff = np.mean(quadrant_diff)

                if avg_diff < 50:
                    issue = "color_mismatch"
                elif avg_diff < 100:
                    issue = "shape_precision"
                else:
                    issue = "missing_details"

                differences.append(
                    {
                        "area": name,
                        "issue": issue,
                        "diff_ratio": float(diff_ratio),
                        "severity": "high" if diff_ratio > 0.1 else "medium",
                    }
                )

        return differences

    def _calculate_quality_score(self, ssim: float, pixel_similarity: float) -> float:
        """Calcula una puntuación de calidad global.

        Args:
            ssim: Valor SSIM.
            pixel_similarity: Valor de similitud de píxeles.

        Returns:
            Puntuación de calidad entre 0 y 1.
        """
        # Ponderar SSIM y similitud de píxeles
        weight_ssim = 0.6
        weight_pixel = 0.4

        quality = (ssim * weight_ssim) + (pixel_similarity * weight_pixel)

        return min(max(quality, 0.0), 1.0)
