"""Tests para el módulo vision."""

import pytest
from pathlib import Path
from PIL import Image
from vectorizer.vision import VisionAnalyzer
from vectorizer.models import ImageAnalysis


@pytest.fixture
def temp_image(tmp_path):
    """Crea una imagen temporal de prueba."""
    img_path = tmp_path / "test.png"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)
    return str(img_path)


class TestInit:
    """Tests para inicialización."""

    def test_init_anthropic(self):
        """Test inicialización con Anthropic."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        assert analyzer.provider == "anthropic"
        assert analyzer.client is not None

    def test_init_openai(self):
        """Test inicialización con OpenAI."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="openai")
        assert analyzer.provider == "openai"
        assert analyzer.client is not None

    def test_init_google_new_api(self):
        """Test inicialización con Google (nueva API)."""
        try:
            analyzer = VisionAnalyzer(api_key="test-key", provider="google")
            assert analyzer.provider == "google"
        except ImportError:
            pytest.skip("google.genai no instalado")

    def test_init_unsupported_provider(self):
        """Test que lanza error con proveedor no soportado."""
        with pytest.raises(ValueError, match="Proveedor no soportado"):
            VisionAnalyzer(api_key="test-key", provider="invalid")


class TestEncodeImage:
    """Tests para _encode_image."""

    def test_encode_png(self, temp_image):
        """Test codificación de PNG."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        media_type, base64_data, pil_image = analyzer._encode_image(Path(temp_image))
        
        assert media_type == "image/png"
        assert len(base64_data) > 0
        assert isinstance(pil_image, Image.Image)

    def test_encode_jpg(self, tmp_path):
        """Test codificación de JPG."""
        img_path = tmp_path / "test.jpg"
        Image.new("RGB", (100, 100), color="blue").save(img_path)
        
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        media_type, _, _ = analyzer._encode_image(Path(img_path))
        
        assert media_type == "image/jpeg"


class TestGetMediaType:
    """Tests para _get_media_type."""

    def test_get_media_type_png(self):
        """Test tipo MIME para PNG."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        assert analyzer._get_media_type(".png") == "image/png"

    def test_get_media_type_jpg(self):
        """Test tipo MIME para JPG."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        assert analyzer._get_media_type(".jpg") == "image/jpeg"
        assert analyzer._get_media_type(".jpeg") == "image/jpeg"

    def test_get_media_type_webp(self):
        """Test tipo MIME para WEBP."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        assert analyzer._get_media_type(".webp") == "image/webp"

    def test_get_media_type_case_insensitive(self):
        """Test que es case-insensitive."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        assert analyzer._get_media_type(".PNG") == "image/png"

    def test_get_media_type_unsupported(self):
        """Test que lanza error con formato no soportado."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        with pytest.raises(ValueError, match="Formato no soportado"):
            analyzer._get_media_type(".xyz")


class TestCreateAnalysisPrompt:
    """Tests para _create_analysis_prompt."""

    def test_create_prompt_medium(self):
        """Test creación de prompt nivel medio."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        prompt = analyzer._create_analysis_prompt("medium")
        
        assert "Analiza esta imagen" in prompt
        assert "JSON" in prompt
        assert "shapes" in prompt
        assert "colors" in prompt

    def test_create_prompt_high(self):
        """Test creación de prompt nivel alto."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        prompt = analyzer._create_analysis_prompt("high")
        
        # El prompt actual usa few-shot examples y solicita análisis estructurado
        assert "Analiza esta imagen" in prompt
        assert "JSON" in prompt
        assert "shapes" in prompt
        assert "colors" in prompt



class TestParseAnalysisResponse:
    """Tests para _parse_analysis_response."""

    def test_parse_valid_json(self):
        """Test parseo de JSON válido."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        response = """{
            "shapes": ["circle", "rectangle"],
            "colors": ["#FF0000", "#00FF00"],
            "composition": "centered",
            "complexity": "simple",
            "style": "flat",
            "description": "Test image"
        }"""
        
        result = analyzer._parse_analysis_response(response)
        
        assert isinstance(result, ImageAnalysis)
        assert result.shapes == ["circle", "rectangle"]
        assert result.colors == ["#FF0000", "#00FF00"]
        assert result.composition == "centered"

    def test_parse_json_with_text(self):
        """Test parseo de JSON con texto alrededor."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        response = """Here is the analysis:
        {
            "shapes": ["circle"],
            "colors": ["#FF0000"],
            "composition": "centered",
            "complexity": "simple",
            "style": "flat",
            "description": "Test"
        }
        Hope this helps!"""
        
        result = analyzer._parse_analysis_response(response)
        
        assert isinstance(result, ImageAnalysis)
        assert result.shapes == ["circle"]

    def test_parse_invalid_json_fallback(self):
        """Test fallback cuando JSON es inválido."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        response = "This is not JSON at all"
        
        result = analyzer._parse_analysis_response(response)
        
        assert isinstance(result, ImageAnalysis)
        assert result.shapes == []
        assert result.composition == "desconocida"
        assert "This is not JSON" in result.description

    def test_parse_partial_json(self):
        """Test parseo de JSON parcial."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        response = """{
            "shapes": ["circle"],
            "colors": ["#FF0000"]
        }"""
        
        result = analyzer._parse_analysis_response(response)
        
        assert result.shapes == ["circle"]
        assert result.composition == "desconocida"  # Valor por defecto


class TestAnalyze:
    """Tests para analyze (requiere mocking de APIs)."""

    def test_analyze_file_not_found(self):
        """Test que lanza error si archivo no existe."""
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        
        with pytest.raises(FileNotFoundError):
            import asyncio
            asyncio.run(analyzer.analyze("/path/that/does/not/exist.png"))

    @pytest.mark.asyncio
    async def test_analyze_with_mock_anthropic(self, temp_image):
        """Test analyze con mock de Anthropic."""
        from unittest.mock import Mock, patch
        
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        
        mock_response = Mock()
        mock_response.content = [Mock(text='{"shapes": ["circle"], "colors": ["#FF0000"], "composition": "centered", "complexity": "simple", "style": "flat", "description": "Test"}')]
        
        with patch.object(analyzer.client.messages, 'create', return_value=mock_response):
            result = await analyzer.analyze(temp_image)
            
            assert isinstance(result, ImageAnalysis)
            assert result.shapes == ["circle"]
            assert result.colors == ["#FF0000"]

    @pytest.mark.asyncio
    async def test_analyze_with_mock_openai(self, temp_image):
        """Test analyze con mock de OpenAI."""
        from unittest.mock import Mock, patch
        
        analyzer = VisionAnalyzer(api_key="test-key", provider="openai")
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='{"shapes": [], "colors": [], "composition": "test", "complexity": "simple", "style": "flat", "description": "Test"}'))]
        
        with patch.object(analyzer.client.chat.completions, 'create', return_value=mock_response):
            result = await analyzer.analyze(temp_image)
            
            assert isinstance(result, ImageAnalysis)

    @pytest.mark.asyncio
    async def test_analyze_detail_levels(self, temp_image):
        """Test diferentes niveles de detalle."""
        from unittest.mock import Mock, patch
        
        analyzer = VisionAnalyzer(api_key="test-key", provider="anthropic")
        
        mock_response = Mock()
        mock_response.content = [Mock(text='{"shapes": [], "colors": [], "composition": "test", "complexity": "simple", "style": "flat", "description": "Test"}')]
        
        with patch.object(analyzer.client.messages, 'create', return_value=mock_response):
            # Test low detail
            result = await analyzer.analyze(temp_image, detail_level="low")
            assert isinstance(result, ImageAnalysis)
            
            # Test high detail
            result = await analyzer.analyze(temp_image, detail_level="high")
            assert isinstance(result, ImageAnalysis)
