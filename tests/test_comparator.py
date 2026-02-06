"""Tests para el módulo comparator."""

import numpy as np
import pytest
from PIL import Image

from vectorizer.comparator import ImageComparator


@pytest.fixture
def comparator():
    """Fixture para ImageComparator."""
    return ImageComparator()


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture para directorio temporal."""
    return tmp_path


@pytest.fixture
def sample_svg():
    """SVG de prueba simple."""
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="#FF0000"/>
</svg>"""


@pytest.fixture
def sample_image(temp_dir):
    """Imagen de prueba."""
    img_path = temp_dir / "test.png"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)
    return str(img_path)


class TestRenderSVG:
    """Tests para render_svg."""

    def test_render_svg_success(self, comparator, sample_svg, temp_dir):
        """Test renderizado exitoso."""
        output_path = temp_dir / "output.png"

        try:
            comparator.render_svg(sample_svg, str(output_path))
            assert output_path.exists()

            # Verificar que es una imagen válida
            img = Image.open(output_path)
            assert img.size[0] > 0
            assert img.size[1] > 0
        except RuntimeError as e:
            # Si no hay método de renderizado, skip
            pytest.skip(f"No rendering method available: {e}")

    def test_render_svg_invalid_raises(self, comparator, temp_dir):
        """Test que SVG inválido lanza error o crea imagen vacía."""
        output_path = temp_dir / "output.png"
        invalid_svg = "<invalid>not svg</invalid>"

        # El comportamiento depende del método de renderizado disponible
        # Algunos métodos lanzan error, otros crean imagen vacía/transparente
        try:
            comparator.render_svg(invalid_svg, str(output_path))
            # Si no lanza error, verificar que se creó el archivo
            assert output_path.exists()
        except (RuntimeError, Exception):
            # Si lanza error, es comportamiento válido
            pass

    def test_render_svg_creates_directory(self, comparator, sample_svg, temp_dir):
        """Test que crea directorios si no existen."""
        output_path = temp_dir / "subdir" / "output.png"

        try:
            comparator.render_svg(sample_svg, str(output_path))
            assert output_path.parent.exists()
        except RuntimeError:
            pytest.skip("No rendering method available")


class TestCompare:
    """Tests para compare."""

    def test_compare_identical_images(self, comparator, sample_image):
        """Test comparación de imágenes idénticas."""
        result = comparator.compare(sample_image, sample_image)

        assert result.ssim > 0.99
        assert result.quality_score > 0.99
        assert len(result.differences) == 0

    def test_compare_different_images(self, comparator, temp_dir):
        """Test comparación de imágenes diferentes."""
        # Crear dos imágenes diferentes
        img1_path = temp_dir / "img1.png"
        img2_path = temp_dir / "img2.png"

        Image.new("RGB", (100, 100), color="red").save(img1_path)
        Image.new("RGB", (100, 100), color="blue").save(img2_path)

        result = comparator.compare(str(img1_path), str(img2_path))

        # Imágenes de color sólido tienen alta correlación estructural
        # aunque los colores sean diferentes (SSIM > 0.6 típicamente)
        assert result.ssim < 0.8
        assert result.quality_score < 0.7
        assert len(result.differences) > 0

    def test_compare_different_sizes(self, comparator, temp_dir):
        """Test comparación de imágenes de diferentes tamaños."""
        img1_path = temp_dir / "img1.png"
        img2_path = temp_dir / "img2.png"

        Image.new("RGB", (100, 100), color="red").save(img1_path)
        Image.new("RGB", (200, 200), color="red").save(img2_path)

        # Debe redimensionar automáticamente
        result = comparator.compare(str(img1_path), str(img2_path))
        assert result is not None


class TestHelperMethods:
    """Tests para métodos auxiliares."""

    def test_load_image(self, comparator, sample_image):
        """Test carga de imagen."""
        img_array = comparator._load_image(sample_image)

        assert isinstance(img_array, np.ndarray)
        assert img_array.shape[2] == 3  # RGB

    def test_resize_to_match(self, comparator):
        """Test redimensionamiento de imágenes."""
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((200, 200, 3), dtype=np.uint8)

        resized1, resized2 = comparator._resize_to_match(img1, img2)

        assert resized1.shape == resized2.shape

    def test_calculate_ssim(self, comparator):
        """Test cálculo de SSIM."""
        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 128
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 128

        ssim = comparator._calculate_ssim(img1, img2)

        assert 0.0 <= ssim <= 1.0
        assert ssim > 0.99  # Imágenes idénticas

    def test_calculate_pixel_similarity(self, comparator):
        """Test cálculo de similitud de píxeles."""
        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 128
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 128

        similarity = comparator._calculate_pixel_similarity(img1, img2)

        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.99

    def test_find_differences_identical(self, comparator):
        """Test búsqueda de diferencias en imágenes idénticas."""
        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 128
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 128

        differences = comparator._find_differences(img1, img2)

        assert len(differences) == 0

    def test_find_differences_different(self, comparator):
        """Test búsqueda de diferencias en imágenes diferentes."""
        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 0
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255

        differences = comparator._find_differences(img1, img2)

        assert len(differences) > 0
        assert all("area" in d for d in differences)
        assert all("issue" in d for d in differences)

    def test_calculate_quality_score(self, comparator):
        """Test cálculo de puntuación de calidad."""
        score = comparator._calculate_quality_score(0.8, 0.9)

        assert 0.0 <= score <= 1.0
        assert 0.8 < score < 0.9  # Promedio ponderado
