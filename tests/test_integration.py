"""Tests de integración end-to-end."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image

from vectorizer.core import Vectorizer
from vectorizer.models import ImageAnalysis, SVGGeneration


@pytest.fixture
def test_image(tmp_path):
    """Crea imagen de prueba."""
    img_path = tmp_path / "test.png"
    Image.new("RGB", (100, 100), color="red").save(img_path)
    return str(img_path)


@pytest.fixture
def output_path(tmp_path):
    """Ruta de salida."""
    return str(tmp_path / "output.svg")


class TestVectorizerIntegration:
    """Tests de integración del flujo completo."""

    @pytest.mark.asyncio
    async def test_vectorize_complete_flow_mock(self, test_image, output_path):
        """Test flujo completo con mocks."""
        vectorizer = Vectorizer(
            api_key="test-key",
            provider="anthropic",
            max_iterations=2,
            quality_threshold=0.9,
        )

        # Mock analyze
        mock_analysis = ImageAnalysis(
            shapes=["circle"],
            colors=["#FF0000"],
            composition="centered",
            complexity="simple",
            style="flat",
            description="Red circle",
        )

        # Mock generate
        mock_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<circle cx="50" cy="50" r="40" fill="red"/></svg>'
        )
        mock_generation = SVGGeneration(svg_code=mock_svg, metadata={"test": True})

        with patch.object(
            vectorizer.vision_analyzer,
            "analyze",
            new_callable=AsyncMock,
            return_value=mock_analysis,
        ):
            with patch.object(
                vectorizer.svg_generator,
                "generate",
                new_callable=AsyncMock,
                return_value=mock_generation,
            ):
                with patch.object(
                    vectorizer.svg_generator,
                    "modify",
                    new_callable=AsyncMock,
                    return_value=mock_generation,
                ):
                    with patch.object(vectorizer.image_comparator, "render_svg"):
                        with patch.object(
                            vectorizer.image_comparator, "compare"
                        ) as mock_compare:
                            # Mock comparison con calidad alta
                            from vectorizer.models import ComparisonResult

                            mock_compare.return_value = ComparisonResult(
                                ssim=0.95,
                                clip_similarity=0.95,
                                quality_score=0.95,
                                differences=[],
                            )

                            result = await vectorizer.vectorize_async(
                                test_image, output_path
                            )

                            assert result is not None
                            assert result.quality >= 0.9
                            assert Path(output_path).exists()

    @pytest.mark.asyncio
    async def test_vectorize_with_iterations(self, test_image, output_path):
        """Test que itera hasta alcanzar calidad."""
        vectorizer = Vectorizer(
            api_key="test-key",
            provider="anthropic",
            max_iterations=3,
            quality_threshold=0.8,
        )

        mock_analysis = ImageAnalysis(
            shapes=[],
            colors=[],
            composition="",
            complexity="",
            style="",
            description="",
        )

        mock_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'
        mock_generation = SVGGeneration(svg_code=mock_svg, metadata={})

        with patch.object(
            vectorizer.vision_analyzer,
            "analyze",
            new_callable=AsyncMock,
            return_value=mock_analysis,
        ):
            with patch.object(
                vectorizer.svg_generator,
                "generate",
                new_callable=AsyncMock,
                return_value=mock_generation,
            ):
                with patch.object(
                    vectorizer.svg_generator,
                    "modify",
                    new_callable=AsyncMock,
                    return_value=mock_generation,
                ):
                    with patch.object(vectorizer.image_comparator, "render_svg"):
                        with patch.object(
                            vectorizer.image_comparator, "compare"
                        ) as mock_compare:
                            from vectorizer.models import ComparisonResult

                            # Simular mejora gradual
                            mock_compare.side_effect = [
                                ComparisonResult(
                                    ssim=0.5,
                                    clip_similarity=0.5,
                                    quality_score=0.5,
                                    differences=[],
                                ),
                                ComparisonResult(
                                    ssim=0.7,
                                    clip_similarity=0.7,
                                    quality_score=0.7,
                                    differences=[],
                                ),
                                ComparisonResult(
                                    ssim=0.85,
                                    clip_similarity=0.85,
                                    quality_score=0.85,
                                    differences=[],
                                ),
                            ]

                            result = await vectorizer.vectorize_async(
                                test_image, output_path
                            )

                            assert result.iterations <= 3
                            assert result.quality >= 0.8

    @pytest.mark.asyncio
    async def test_vectorize_stops_at_threshold(self, test_image, output_path):
        """Test que se detiene al alcanzar threshold."""
        vectorizer = Vectorizer(
            api_key="test-key", max_iterations=10, quality_threshold=0.85
        )

        mock_analysis = ImageAnalysis(
            shapes=[],
            colors=[],
            composition="",
            complexity="",
            style="",
            description="",
        )
        mock_generation = SVGGeneration(
            svg_code='<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>',
            metadata={},
        )

        with patch.object(
            vectorizer.vision_analyzer,
            "analyze",
            new_callable=AsyncMock,
            return_value=mock_analysis,
        ):
            with patch.object(
                vectorizer.svg_generator,
                "generate",
                new_callable=AsyncMock,
                return_value=mock_generation,
            ):
                with patch.object(
                    vectorizer.svg_generator,
                    "modify",
                    new_callable=AsyncMock,
                    return_value=mock_generation,
                ):
                    with patch.object(vectorizer.image_comparator, "render_svg"):
                        with patch.object(
                            vectorizer.image_comparator, "compare"
                        ) as mock_compare:
                            from vectorizer.models import ComparisonResult

                            # Primera iteración alcanza threshold
                            mock_compare.return_value = ComparisonResult(
                                ssim=0.9,
                                clip_similarity=0.9,
                                quality_score=0.9,
                                differences=[],
                            )

                            result = await vectorizer.vectorize_async(
                                test_image, output_path
                            )

                            # Debe detenerse en iteración 1
                            assert result.iterations == 1
                            assert result.quality >= 0.85

    @pytest.mark.asyncio
    async def test_vectorize_with_callback(self, test_image, output_path):
        """Test que callback se llama en cada iteración."""
        vectorizer = Vectorizer(api_key="test-key", max_iterations=2)

        callback_calls = []

        def callback(iteration, quality):
            callback_calls.append((iteration, quality))

        mock_analysis = ImageAnalysis(
            shapes=[],
            colors=[],
            composition="",
            complexity="",
            style="",
            description="",
        )
        mock_generation = SVGGeneration(
            svg_code='<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>',
            metadata={},
        )

        with patch.object(
            vectorizer.vision_analyzer,
            "analyze",
            new_callable=AsyncMock,
            return_value=mock_analysis,
        ):
            with patch.object(
                vectorizer.svg_generator,
                "generate",
                new_callable=AsyncMock,
                return_value=mock_generation,
            ):
                with patch.object(
                    vectorizer.svg_generator,
                    "modify",
                    new_callable=AsyncMock,
                    return_value=mock_generation,
                ):
                    with patch.object(vectorizer.image_comparator, "render_svg"):
                        with patch.object(
                            vectorizer.image_comparator, "compare"
                        ) as mock_compare:
                            from vectorizer.models import ComparisonResult

                            mock_compare.return_value = ComparisonResult(
                                ssim=0.5,
                                clip_similarity=0.5,
                                quality_score=0.5,
                                differences=[],
                            )

                            result = await vectorizer.vectorize_async(
                                test_image, output_path, callback=callback
                            )
                            assert result is not None

                            # Callback debe haberse llamado
                            assert len(callback_calls) == 2
                            assert callback_calls[0][0] == 1
                            assert callback_calls[1][0] == 2

    @pytest.mark.asyncio
    async def test_vectorize_handles_render_error(self, test_image, output_path):
        """Test manejo de error de renderizado."""
        vectorizer = Vectorizer(api_key="test-key", max_iterations=1)

        mock_analysis = ImageAnalysis(
            shapes=[],
            colors=[],
            composition="",
            complexity="",
            style="",
            description="",
        )
        mock_generation = SVGGeneration(
            svg_code='<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>',
            metadata={},
        )

        with patch.object(
            vectorizer.vision_analyzer,
            "analyze",
            new_callable=AsyncMock,
            return_value=mock_analysis,
        ):
            with patch.object(
                vectorizer.svg_generator,
                "generate",
                new_callable=AsyncMock,
                return_value=mock_generation,
            ):
                with patch.object(
                    vectorizer.image_comparator, "render_svg"
                ) as mock_render:
                    # Simular error de renderizado
                    mock_render.side_effect = RuntimeError(
                        "No rendering method available"
                    )

                    with pytest.raises(RuntimeError, match="No rendering method"):
                        await vectorizer.vectorize_async(test_image, output_path)


class TestVectorizerSync:
    """Tests para método síncrono vectorize."""

    def test_vectorize_sync_calls_async(self, test_image, output_path):
        """Test que vectorize llama a vectorize_async."""
        vectorizer = Vectorizer(api_key="test-key")

        with patch.object(
            vectorizer, "vectorize_async", new_callable=AsyncMock
        ) as mock_async:
            from vectorizer.models import VectorizationResult

            mock_async.return_value = VectorizationResult(
                svg_code="<svg></svg>",
                quality=0.8,
                iterations=1,
                metrics={},
                metadata={},
            )

            result = vectorizer.vectorize(test_image, output_path)

            mock_async.assert_called_once()
            assert result is not None
