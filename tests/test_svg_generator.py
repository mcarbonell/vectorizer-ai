"""Tests para el módulo svg_generator."""

import pytest
from vectorizer.svg_generator import SVGGenerator
from vectorizer.models import ImageAnalysis, SVGGeneration



@pytest.fixture
def generator():
    """Fixture para SVGGenerator."""
    return SVGGenerator(api_key="test-key", provider="anthropic")


@pytest.fixture
def sample_analysis():
    """Análisis de imagen de prueba."""
    return ImageAnalysis(
        shapes=["circle", "rectangle"],
        colors=["#FF0000", "#00FF00"],
        composition="centered",
        complexity="simple",
        style="flat",
        description="Test image"
    )


class TestExtractSVG:
    """Tests para _extract_svg."""

    def test_extract_from_markdown_svg(self, generator):
        """Test extracción de markdown code block con svg."""
        response = """```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="red"/>
</svg>
```"""
        svg = generator._extract_svg(response)
        assert "<svg" in svg
        assert "<circle" in svg
        assert "```" not in svg

    def test_extract_from_markdown_xml(self, generator):
        """Test extracción de markdown code block con xml."""
        response = """```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="blue"/>
</svg>
```"""
        svg = generator._extract_svg(response)
        assert "<svg" in svg
        assert "<rect" in svg

    def test_extract_from_markdown_no_lang(self, generator):
        """Test extracción de markdown code block sin lenguaje."""
        response = """```
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100"/>
</svg>
```"""
        svg = generator._extract_svg(response)
        assert "<svg" in svg

    def test_extract_plain_svg(self, generator):
        """Test extracción de SVG sin markdown."""
        response = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'
        svg = generator._extract_svg(response)
        assert svg == response

    def test_extract_svg_with_text(self, generator):
        """Test extracción de SVG con texto alrededor."""
        response = """Here is your SVG:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40"/>
</svg>
Hope this helps!"""
        svg = generator._extract_svg(response)
        assert "<svg" in svg
        assert "<circle" in svg
        assert "Here is" not in svg
        assert "Hope" not in svg

    def test_extract_self_closing_svg(self, generator):
        """Test extracción de SVG auto-cerrado."""
        response = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"/>'
        svg = generator._extract_svg(response)
        assert "<svg" in svg

    def test_extract_case_insensitive(self, generator):
        """Test extracción case-insensitive."""
        response = '<SVG xmlns="http://www.w3.org/2000/svg"><RECT/></SVG>'
        svg = generator._extract_svg(response)
        assert "svg" in svg.lower()

    def test_extract_no_svg_raises(self, generator):
        """Test que lanza error si no hay SVG."""
        response = "This is just text without any SVG code"
        with pytest.raises(ValueError, match="No se encontró código SVG"):
            generator._extract_svg(response)

    def test_extract_invalid_tags_raises(self, generator):
        """Test que lanza error con tags inválidos."""
        response = "<div>Not an SVG</div>"
        with pytest.raises(ValueError):
            generator._extract_svg(response)


class TestValidateSVG:
    """Tests para _validate_svg."""

    def test_validate_valid_svg(self, generator):
        """Test validación de SVG válido."""
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'
        assert generator._validate_svg(svg) is True

    def test_validate_empty_string(self, generator):
        """Test validación de string vacío."""
        assert generator._validate_svg("") is False
        assert generator._validate_svg("   ") is False

    def test_validate_no_opening_tag(self, generator):
        """Test validación sin etiqueta de apertura."""
        svg = '<rect/></svg>'
        assert generator._validate_svg(svg) is False

    def test_validate_no_closing_tag(self, generator):
        """Test validación sin etiqueta de cierre."""
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/>'
        assert generator._validate_svg(svg) is False

    def test_validate_self_closing_empty(self, generator):
        """Test validación de SVG auto-cerrado vacío."""
        svg = '<svg xmlns="http://www.w3.org/2000/svg"/>'
        assert generator._validate_svg(svg) is False

    def test_validate_without_xmlns(self, generator):
        """Test validación sin xmlns (warning pero acepta)."""
        svg = '<svg viewBox="0 0 100 100"><rect/></svg>'
        # Debe aceptar pero con warning
        result = generator._validate_svg(svg)
        assert result is True  # Acepta pero logea warning

    def test_validate_case_insensitive(self, generator):
        """Test validación case-insensitive."""
        svg = '<SVG xmlns="http://www.w3.org/2000/svg"><RECT/></SVG>'
        assert generator._validate_svg(svg) is True


class TestOptimize:
    """Tests para optimize."""

    def test_optimize_removes_comments(self, generator):
        """Test que elimina comentarios."""
        svg = '<svg><!-- comment --><rect/></svg>'
        optimized = generator.optimize(svg)
        assert "<!--" not in optimized
        assert "comment" not in optimized

    def test_optimize_removes_whitespace(self, generator):
        """Test que elimina espacios extra."""
        svg = '<svg>  <rect/>  </svg>'
        optimized = generator.optimize(svg, level="medium")
        assert optimized == '<svg><rect/></svg>'

    def test_optimize_low_level(self, generator):
        """Test optimización nivel bajo."""
        svg = '<svg><!-- comment --><rect/></svg>'
        optimized = generator.optimize(svg, level="low")
        assert "<!--" not in optimized

    def test_optimize_high_level(self, generator):
        """Test optimización nivel alto."""
        svg = '<svg fill="none" stroke="none"><rect/></svg>'
        optimized = generator.optimize(svg, level="high")
        assert 'fill="none"' not in optimized


class TestCreateFallbackSVG:
    """Tests para _create_fallback_svg."""

    def test_fallback_with_colors(self, generator, sample_analysis):
        """Test fallback con colores."""
        svg = generator._create_fallback_svg(sample_analysis)
        assert "<svg" in svg
        assert "#FF0000" in svg  # Primer color

    def test_fallback_without_colors(self, generator):
        """Test fallback sin colores."""
        analysis = ImageAnalysis(
            shapes=[],
            colors=[],
            composition="",
            complexity="",
            style="",
            description=""
        )
        svg = generator._create_fallback_svg(analysis)
        assert "<svg" in svg
        assert "#000000" in svg  # Color por defecto


class TestGenerateAndModify:
    """Tests para generate y modify con mocks."""

    @pytest.mark.asyncio
    async def test_generate_with_mock(self, sample_analysis):
        """Test generate con mock de API."""
        from unittest.mock import Mock, patch
        
        generator = SVGGenerator(api_key="test-key", provider="anthropic")
        
        mock_response = Mock()
        mock_response.content = [Mock(text='<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>')]
        
        with patch.object(generator.anthropic_client.messages, 'create', return_value=mock_response):
            result = await generator.generate(sample_analysis)
            
            assert isinstance(result, SVGGeneration)
            assert "<svg" in result.svg_code

    @pytest.mark.asyncio
    async def test_generate_with_invalid_response(self, sample_analysis):
        """Test generate con respuesta inválida usa fallback."""
        from unittest.mock import Mock, patch
        
        generator = SVGGenerator(api_key="test-key", provider="anthropic")
        
        mock_response = Mock()
        mock_response.content = [Mock(text='This is not SVG')]
        
        with patch.object(generator.anthropic_client.messages, 'create', return_value=mock_response):
            result = await generator.generate(sample_analysis)
            
            # Debe usar fallback
            assert isinstance(result, SVGGeneration)
            assert "<svg" in result.svg_code

    @pytest.mark.asyncio
    async def test_modify_with_mock(self):
        """Test modify con mock de API."""
        from unittest.mock import Mock, patch
        
        generator = SVGGenerator(api_key="test-key", provider="anthropic")
        
        original_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'
        mock_response = Mock()
        mock_response.content = [Mock(text='<svg xmlns="http://www.w3.org/2000/svg"><circle/></svg>')]
        
        with patch.object(generator.anthropic_client.messages, 'create', return_value=mock_response):
            result = await generator.modify(original_svg, ["Add circle"])
            
            assert isinstance(result, SVGGeneration)
            assert "<svg" in result.svg_code

    @pytest.mark.asyncio
    async def test_modify_with_invalid_response_returns_original(self):
        """Test modify con respuesta inválida retorna original."""
        from unittest.mock import Mock, patch
        
        generator = SVGGenerator(api_key="test-key", provider="anthropic")
        
        original_svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>'
        mock_response = Mock()
        mock_response.content = [Mock(text='Invalid response')]
        
        with patch.object(generator.anthropic_client.messages, 'create', return_value=mock_response):
            result = await generator.modify(original_svg, ["Change"])
            
            # Debe retornar original
            assert result.svg_code == original_svg
