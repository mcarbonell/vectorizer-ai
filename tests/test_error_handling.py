"""Tests para manejo de errores y reintentos."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from vectorizer.vision import VisionAnalyzer
from vectorizer.svg_generator import SVGGenerator
from vectorizer.models import ImageAnalysis


class TestVisionAnalyzerRetries:
    """Tests para reintentos en VisionAnalyzer."""

    @pytest.mark.asyncio
    async def test_anthropic_retry_on_connection_error(self):
        """Test que reintenta en ConnectionError."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        
        # Mock que falla 2 veces y luego funciona
        mock_response = Mock()
        mock_response.content = [Mock(text='{"shapes": [], "colors": []}')]
        
        with patch.object(analyzer.client.messages, 'create') as mock_create:
            mock_create.side_effect = [
                ConnectionError("Network error"),
                ConnectionError("Network error"),
                mock_response
            ]
            
            image_data = ("image/png", "base64data", Mock())
            result = await analyzer._call_anthropic(image_data, "test prompt")
            
            assert mock_create.call_count == 3
            assert result == '{"shapes": [], "colors": []}'

    @pytest.mark.asyncio
    async def test_anthropic_fails_after_max_retries(self):
        """Test que falla después de máximo de reintentos."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        
        with patch.object(analyzer.client.messages, 'create') as mock_create:
            mock_create.side_effect = ConnectionError("Network error")
            
            image_data = ("image/png", "base64data", Mock())
            
            with pytest.raises(ConnectionError):
                await analyzer._call_anthropic(image_data, "test prompt")
            
            assert mock_create.call_count == 3  # 3 intentos


class TestSVGGeneratorRetries:
    """Tests para reintentos en SVGGenerator."""

    @pytest.mark.asyncio
    async def test_anthropic_retry_success(self):
        """Test reintento exitoso en SVGGenerator."""
        generator = SVGGenerator(api_key="test-key", provider="anthropic")
        
        mock_response = Mock()
        mock_response.content = [Mock(text='<svg></svg>')]
        
        with patch.object(generator.anthropic_client.messages, 'create') as mock_create:
            mock_create.side_effect = [
                TimeoutError("Timeout"),
                mock_response
            ]
            
            result = await generator._call_anthropic("test prompt")
            
            assert mock_create.call_count == 2
            assert result == '<svg></svg>'

    @pytest.mark.asyncio
    async def test_openai_retry_on_timeout(self):
        """Test reintento en timeout para OpenAI."""
        generator = SVGGenerator(api_key="test-key", provider="openai")
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='<svg></svg>'))]
        
        with patch.object(generator.openai_client.chat.completions, 'create') as mock_create:
            mock_create.side_effect = [
                TimeoutError("Timeout"),
                mock_response
            ]
            
            result = await generator._call_openai("test prompt")
            
            assert mock_create.call_count == 2
            assert result == '<svg></svg>'


class TestErrorLogging:
    """Tests para logging de errores."""

    @pytest.mark.asyncio
    async def test_error_logged_on_failure(self):
        """Test que los errores se loguean correctamente."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        
        with patch.object(analyzer.client.messages, 'create') as mock_create:
            mock_create.side_effect = ValueError("Invalid input")
            
            image_data = ("image/png", "base64data", Mock())
            
            with pytest.raises(ValueError):
                await analyzer._call_anthropic(image_data, "test prompt")


class TestFileNotFoundHandling:
    """Tests para manejo de archivos no encontrados."""

    @pytest.mark.asyncio
    async def test_analyze_file_not_found(self):
        """Test que lanza FileNotFoundError apropiadamente."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        
        with pytest.raises(FileNotFoundError, match="Archivo no encontrado"):
            await analyzer.analyze("/nonexistent/path.png")

    def test_get_media_type_unsupported_format(self):
        """Test que lanza ValueError para formato no soportado."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        
        with pytest.raises(ValueError, match="Formato no soportado"):
            analyzer._get_media_type(".invalid")


class TestSVGExtractionErrors:
    """Tests para errores en extracción de SVG."""

    def test_extract_svg_no_svg_found(self):
        """Test que lanza ValueError si no hay SVG."""
        generator = SVGGenerator(api_key="test-key", provider="anthropic")
        
        with pytest.raises(ValueError, match="No se encontró código SVG"):
            generator._extract_svg("This is just text without SVG")

    def test_validate_svg_empty_string(self):
        """Test validación de string vacío."""
        generator = SVGGenerator(api_key="test-key", provider="anthropic")
        
        assert generator._validate_svg("") is False
        assert generator._validate_svg("   ") is False

    def test_validate_svg_no_closing_tag(self):
        """Test validación sin etiqueta de cierre."""
        generator = SVGGenerator(api_key="test-key", provider="anthropic")
        
        assert generator._validate_svg('<svg xmlns="http://www.w3.org/2000/svg">') is False
