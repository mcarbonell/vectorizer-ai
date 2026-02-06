"""Tests para CLI."""

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner
from PIL import Image

from vectorizer.cli import main


@pytest.fixture
def runner():
    """CLI runner."""
    return CliRunner()


@pytest.fixture
def test_image(tmp_path):
    """Imagen de prueba."""
    img_path = tmp_path / "test.png"
    Image.new("RGB", (100, 100), color="red").save(img_path)
    return str(img_path)


class TestCLIBasic:
    """Tests básicos de CLI."""

    def test_cli_no_args(self, runner):
        """Test CLI sin argumentos muestra ayuda."""
        result = runner.invoke(main, [])
        assert result.exit_code != 0

    def test_cli_help(self, runner):
        """Test --help funciona."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_cli_missing_api_key(self, runner, test_image, tmp_path):
        """Test que falla sin API key."""
        output = str(tmp_path / "output.svg")

        with patch.dict("os.environ", {}, clear=True):
            result = runner.invoke(main, [test_image, output])
            assert result.exit_code != 0
            assert "API key no encontrada" in result.output


class TestCLIValidation:
    """Tests de validación en CLI."""

    def test_cli_invalid_max_iterations(self, runner, test_image, tmp_path):
        """Test que rechaza max-iterations inválido."""
        output = str(tmp_path / "output.svg")

        result = runner.invoke(
            main, [test_image, output, "--api-key", "test-key", "--max-iterations", "0"]
        )
        assert result.exit_code != 0
        assert "max-iterations debe estar entre 1 y 100" in result.output

    def test_cli_invalid_quality_threshold(self, runner, test_image, tmp_path):
        """Test que rechaza quality-threshold inválido."""
        output = str(tmp_path / "output.svg")

        result = runner.invoke(
            main,
            [test_image, output, "--api-key", "test-key", "--quality-threshold", "1.5"],
        )
        assert result.exit_code != 0
        assert "quality-threshold debe estar entre 0.0 y 1.0" in result.output

    def test_cli_file_not_found(self, runner, tmp_path):
        """Test que falla con archivo no existente."""
        output = str(tmp_path / "output.svg")

        result = runner.invoke(
            main, ["/nonexistent/file.png", output, "--api-key", "test-key"]
        )
        assert result.exit_code != 0


class TestCLIOptions:
    """Tests de opciones de CLI."""

    def test_cli_with_provider(self, runner, test_image, tmp_path):
        """Test opción --provider."""
        output = str(tmp_path / "output.svg")

        with patch("vectorizer.cli.Vectorizer") as mock_vectorizer:
            mock_instance = Mock()
            mock_vectorizer.return_value = mock_instance

            from vectorizer.models import VectorizationResult

            mock_instance.vectorize.return_value = VectorizationResult(
                svg_code="<svg></svg>",
                quality=0.8,
                iterations=1,
                metrics={},
                metadata={},
            )

            result = runner.invoke(
                main,
                [test_image, output, "--api-key", "test-key", "--provider", "google"],
            )
            assert result.exit_code == 0

            # Verificar que se llamó con provider correcto
            mock_vectorizer.assert_called_once()
            call_kwargs = mock_vectorizer.call_args[1]
            assert call_kwargs["provider"] == "google"

    def test_cli_with_model(self, runner, test_image, tmp_path):
        """Test opción --model."""
        output = str(tmp_path / "output.svg")

        with patch("vectorizer.cli.Vectorizer") as mock_vectorizer:
            mock_instance = Mock()
            mock_vectorizer.return_value = mock_instance

            from vectorizer.models import VectorizationResult

            mock_instance.vectorize.return_value = VectorizationResult(
                svg_code="<svg></svg>",
                quality=0.8,
                iterations=1,
                metrics={},
                metadata={},
            )

            result = runner.invoke(
                main,
                [
                    test_image,
                    output,
                    "--api-key",
                    "test-key",
                    "--model",
                    "gpt-4-vision-preview",
                ],
            )
            assert result.exit_code == 0

            mock_vectorizer.assert_called_once()
            call_kwargs = mock_vectorizer.call_args[1]
            assert call_kwargs["model"] == "gpt-4-vision-preview"

    def test_cli_verbose(self, runner, test_image, tmp_path):
        """Test opción --verbose."""
        output = str(tmp_path / "output.svg")

        with patch("vectorizer.cli.Vectorizer") as mock_vectorizer:
            mock_instance = Mock()
            mock_vectorizer.return_value = mock_instance

            from vectorizer.models import VectorizationResult

            mock_instance.vectorize.return_value = VectorizationResult(
                svg_code="<svg></svg>",
                quality=0.8,
                iterations=1,
                metrics={},
                metadata={},
            )

            result = runner.invoke(
                main, [test_image, output, "--api-key", "test-key", "--verbose"]
            )
            assert result.exit_code == 0

            mock_vectorizer.assert_called_once()
            call_kwargs = mock_vectorizer.call_args[1]
            assert call_kwargs["verbose"] is True


class TestCLIOutput:
    """Tests de output de CLI."""

    def test_cli_shows_progress(self, runner, test_image, tmp_path):
        """Test que muestra progreso."""
        output = str(tmp_path / "output.svg")

        with patch("vectorizer.cli.Vectorizer") as mock_vectorizer:
            mock_instance = Mock()
            mock_vectorizer.return_value = mock_instance

            from vectorizer.models import VectorizationResult

            mock_instance.vectorize.return_value = VectorizationResult(
                svg_code="<svg></svg>",
                quality=0.85,
                iterations=3,
                metrics={"ssim": 0.8, "clip_similarity": 0.9},
                metadata={},
            )

            result = runner.invoke(main, [test_image, output, "--api-key", "test-key"])

            assert "Vectorizacion completada" in result.output
            assert "Iteraciones: 3" in result.output
            assert "Calidad final: 0.85" in result.output
