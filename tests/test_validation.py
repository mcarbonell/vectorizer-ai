"""Tests para validación de entrada."""

import pytest
from PIL import Image

from vectorizer.core import Vectorizer


class TestVectorizerInit:
    """Tests para validación en __init__."""

    def test_init_empty_api_key(self):
        """Test que rechaza API key vacía."""
        with pytest.raises(ValueError, match="API key no puede estar vacía"):
            Vectorizer(api_key="")

    def test_init_whitespace_api_key(self):
        """Test que rechaza API key solo con espacios."""
        with pytest.raises(ValueError, match="API key no puede estar vacía"):
            Vectorizer(api_key="   ")

    def test_init_invalid_max_iterations_low(self):
        """Test que rechaza max_iterations < 1."""
        with pytest.raises(ValueError, match="max_iterations debe estar entre 1 y 100"):
            Vectorizer(api_key="test-key", max_iterations=0)

    def test_init_invalid_max_iterations_high(self):
        """Test que rechaza max_iterations > 100."""
        with pytest.raises(ValueError, match="max_iterations debe estar entre 1 y 100"):
            Vectorizer(api_key="test-key", max_iterations=101)

    def test_init_invalid_quality_threshold_low(self):
        """Test que rechaza quality_threshold < 0."""
        with pytest.raises(
            ValueError, match="quality_threshold debe estar entre 0.0 y 1.0"
        ):
            Vectorizer(api_key="test-key", quality_threshold=-0.1)

    def test_init_invalid_quality_threshold_high(self):
        """Test que rechaza quality_threshold > 1."""
        with pytest.raises(
            ValueError, match="quality_threshold debe estar entre 0.0 y 1.0"
        ):
            Vectorizer(api_key="test-key", quality_threshold=1.1)

    def test_init_invalid_provider(self):
        """Test que rechaza proveedor no soportado."""
        with pytest.raises(ValueError, match="Proveedor no soportado"):
            Vectorizer(api_key="test-key", provider="invalid")

    def test_init_valid_parameters(self):
        """Test que acepta parámetros válidos."""
        vectorizer = Vectorizer(
            api_key="test-key",
            max_iterations=5,
            quality_threshold=0.8,
            provider="anthropic",
        )
        assert vectorizer.max_iterations == 5
        assert vectorizer.quality_threshold == 0.8


class TestVectorizeValidation:
    """Tests para validación en vectorize."""

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        """Test que lanza FileNotFoundError."""
        vectorizer = Vectorizer(api_key="test-key")

        with pytest.raises(FileNotFoundError, match="Archivo no encontrado"):
            await vectorizer.vectorize_async("/nonexistent/file.png", "output.svg")

    @pytest.mark.asyncio
    async def test_input_is_directory(self, tmp_path):
        """Test que rechaza directorio como entrada."""
        vectorizer = Vectorizer(api_key="test-key")
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        with pytest.raises(ValueError, match="La ruta no es un archivo"):
            await vectorizer.vectorize_async(str(test_dir), "output.svg")

    @pytest.mark.asyncio
    async def test_unsupported_format(self, tmp_path):
        """Test que rechaza formato no soportado."""
        vectorizer = Vectorizer(api_key="test-key")
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        with pytest.raises(ValueError, match="Formato no soportado"):
            await vectorizer.vectorize_async(str(test_file), "output.svg")

    @pytest.mark.asyncio
    async def test_file_too_large(self, tmp_path):
        """Test que rechaza archivo muy grande."""
        vectorizer = Vectorizer(api_key="test-key")
        test_file = tmp_path / "large.png"

        # Crear archivo de 11MB (más del límite de 10MB)
        large_data = b"0" * (11 * 1024 * 1024)
        test_file.write_bytes(large_data)

        with pytest.raises(ValueError, match="Archivo muy grande"):
            await vectorizer.vectorize_async(str(test_file), "output.svg")

    @pytest.mark.asyncio
    async def test_output_is_directory(self, tmp_path):
        """Test que rechaza directorio como salida."""
        vectorizer = Vectorizer(api_key="test-key")

        # Crear imagen válida
        img_file = tmp_path / "test.png"
        Image.new("RGB", (100, 100), color="red").save(img_file)

        # Crear directorio como salida
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with pytest.raises(ValueError, match="La ruta de salida no es un archivo"):
            await vectorizer.vectorize_async(str(img_file), str(output_dir))

    @pytest.mark.asyncio
    async def test_valid_png_file(self, tmp_path):
        """Test que acepta archivo PNG válido."""
        vectorizer = Vectorizer(api_key="test-key")

        img_file = tmp_path / "test.png"
        Image.new("RGB", (100, 100), color="red").save(img_file)

        # Solo validar que no lanza error de validación
        # (fallará en la llamada a API pero eso es esperado)
        try:
            await vectorizer.vectorize_async(
                str(img_file), str(tmp_path / "output.svg")
            )
        except Exception as e:
            # Debe fallar por API, no por validación
            assert "Archivo no encontrado" not in str(e)
            assert "Formato no soportado" not in str(e)
            assert "muy grande" not in str(e)


class TestSupportedFormats:
    """Tests para formatos soportados."""

    @pytest.mark.asyncio
    async def test_png_supported(self, tmp_path):
        """Test que PNG es soportado."""
        vectorizer = Vectorizer(api_key="test-key")
        img_file = tmp_path / "test.png"
        Image.new("RGB", (100, 100)).save(img_file)

        try:
            await vectorizer.vectorize_async(str(img_file), str(tmp_path / "out.svg"))
        except ValueError as e:
            assert "Formato no soportado" not in str(e)
        except Exception:
            pass  # Otros errores son esperados

    @pytest.mark.asyncio
    async def test_jpg_supported(self, tmp_path):
        """Test que JPG es soportado."""
        vectorizer = Vectorizer(api_key="test-key")
        img_file = tmp_path / "test.jpg"
        Image.new("RGB", (100, 100)).save(img_file)

        try:
            await vectorizer.vectorize_async(str(img_file), str(tmp_path / "out.svg"))
        except ValueError as e:
            assert "Formato no soportado" not in str(e)
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_webp_supported(self, tmp_path):
        """Test que WEBP es soportado."""
        vectorizer = Vectorizer(api_key="test-key")
        img_file = tmp_path / "test.webp"
        Image.new("RGB", (100, 100)).save(img_file, "WEBP")

        try:
            await vectorizer.vectorize_async(str(img_file), str(tmp_path / "out.svg"))
        except ValueError as e:
            assert "Formato no soportado" not in str(e)
        except Exception:
            pass
