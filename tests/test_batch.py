"""Tests para el modo batch de Vectorizer AI."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from vectorizer import Vectorizer, BatchResult


@pytest.fixture
def vectorizer():
    """Fixture para crear instancia de Vectorizer."""
    return Vectorizer(
        api_key="test-key",
        model="test-model",
        max_iterations=3,
        quality_threshold=0.8,
        provider="anthropic",
    )


@pytest.fixture
def mock_vectorize_async():
    """Mock para vectorize_async."""
    async def mock_vectorize(input_path, output_path, callback=None):
        from vectorizer.models import VectorizationResult
        
        # Simular callback
        if callback:
            callback(1, 0.85)
        
        return VectorizationResult(
            svg_code="<svg>test</svg>",
            quality=0.85,
            iterations=2,
            metrics={"ssim": 0.80, "clip_similarity": 0.90},
            metadata={"input_path": input_path, "output_path": output_path},
        )
    
    return mock_vectorize


class TestBatchBasic:
    """Tests básicos del modo batch."""
    
    def test_batch_with_list(self, vectorizer, mock_vectorize_async, tmp_path):
        """Test: Procesar lista de archivos."""
        # Crear archivos de prueba
        input_files = []
        for i in range(3):
            file = tmp_path / f"test{i}.png"
            file.write_bytes(b"fake image")
            input_files.append(str(file))
        
        output_dir = tmp_path / "output"
        
        with patch.object(vectorizer, 'vectorize_async', mock_vectorize_async):
            result = vectorizer.vectorize_batch(
                input_paths=input_files,
                output_dir=str(output_dir),
            )
        
        assert isinstance(result, BatchResult)
        assert result.total == 3
        assert result.successful == 3
        assert result.failed == 0
        assert len(result.results) == 3
        assert len(result.errors) == 0
    
    def test_batch_with_glob(self, vectorizer, mock_vectorize_async, tmp_path):
        """Test: Procesar archivos con patrón glob."""
        # Crear archivos de prueba
        for i in range(3):
            file = tmp_path / f"test{i}.png"
            file.write_bytes(b"fake image")
        
        output_dir = tmp_path / "output"
        pattern = str(tmp_path / "*.png")
        
        with patch.object(vectorizer, 'vectorize_async', mock_vectorize_async):
            result = vectorizer.vectorize_batch(
                input_paths=pattern,
                output_dir=str(output_dir),
            )
        
        assert result.total == 3
        assert result.successful == 3
    
    def test_batch_empty_list(self, vectorizer, tmp_path):
        """Test: Lista vacía debe fallar."""
        output_dir = tmp_path / "output"
        
        with pytest.raises(ValueError, match="no puede estar vacío"):
            vectorizer.vectorize_batch(
                input_paths=[],
                output_dir=str(output_dir),
            )
    
    def test_batch_invalid_glob(self, vectorizer, tmp_path):
        """Test: Patrón glob sin resultados debe fallar."""
        output_dir = tmp_path / "output"
        pattern = str(tmp_path / "nonexistent*.png")
        
        with pytest.raises(ValueError, match="No se encontraron archivos"):
            vectorizer.vectorize_batch(
                input_paths=pattern,
                output_dir=str(output_dir),
            )
    
    def test_batch_creates_output_dir(self, vectorizer, mock_vectorize_async, tmp_path):
        """Test: Crear directorio de salida si no existe."""
        input_file = tmp_path / "test.png"
        input_file.write_bytes(b"fake image")
        
        output_dir = tmp_path / "new_output" / "nested"
        
        with patch.object(vectorizer, 'vectorize_async', mock_vectorize_async):
            result = vectorizer.vectorize_batch(
                input_paths=[str(input_file)],
                output_dir=str(output_dir),
            )
        
        assert output_dir.exists()
        assert output_dir.is_dir()
        assert result.successful == 1


class TestBatchCallback:
    """Tests de callbacks en modo batch."""
    
    def test_batch_callback_called(self, vectorizer, mock_vectorize_async, tmp_path):
        """Test: Callback es llamado correctamente."""
        input_file = tmp_path / "test.png"
        input_file.write_bytes(b"fake image")
        output_dir = tmp_path / "output"
        
        callback_calls = []
        
        def callback(filename, current, total, quality):
            callback_calls.append({
                'filename': filename,
                'current': current,
                'total': total,
                'quality': quality,
            })
        
        with patch.object(vectorizer, 'vectorize_async', mock_vectorize_async):
            vectorizer.vectorize_batch(
                input_paths=[str(input_file)],
                output_dir=str(output_dir),
                callback=callback,
            )
        
        assert len(callback_calls) > 0
        assert callback_calls[0]['filename'] == 'test.png'
        assert callback_calls[0]['current'] == 1
        assert callback_calls[0]['total'] == 1
    
    def test_batch_no_callback(self, vectorizer, mock_vectorize_async, tmp_path):
        """Test: Funciona sin callback."""
        input_file = tmp_path / "test.png"
        input_file.write_bytes(b"fake image")
        output_dir = tmp_path / "output"
        
        with patch.object(vectorizer, 'vectorize_async', mock_vectorize_async):
            result = vectorizer.vectorize_batch(
                input_paths=[str(input_file)],
                output_dir=str(output_dir),
                callback=None,
            )
        
        assert result.successful == 1


class TestBatchErrorHandling:
    """Tests de manejo de errores en modo batch."""
    
    def test_batch_continue_on_error(self, vectorizer, tmp_path):
        """Test: Continuar procesando después de error."""
        # Crear archivos de prueba
        files = []
        for i in range(3):
            file = tmp_path / f"test{i}.png"
            file.write_bytes(b"fake image")
            files.append(str(file))
        
        output_dir = tmp_path / "output"
        
        # Mock que falla en el segundo archivo
        call_count = [0]
        
        async def mock_vectorize_with_error(input_path, output_path, callback=None):
            from vectorizer.models import VectorizationResult
            
            call_count[0] += 1
            if call_count[0] == 2:
                raise ValueError("Simulated error")
            
            return VectorizationResult(
                svg_code="<svg>test</svg>",
                quality=0.85,
                iterations=2,
                metrics={},
                metadata={},
            )
        
        with patch.object(vectorizer, 'vectorize_async', mock_vectorize_with_error):
            result = vectorizer.vectorize_batch(
                input_paths=files,
                output_dir=str(output_dir),
                continue_on_error=True,
            )
        
        assert result.total == 3
        assert result.successful == 2
        assert result.failed == 1
        assert len(result.errors) == 1
        assert "Simulated error" in result.errors[0]['error']
    
    def test_batch_stop_on_error(self, vectorizer, tmp_path):
        """Test: Detener procesamiento en error."""
        files = []
        for i in range(3):
            file = tmp_path / f"test{i}.png"
            file.write_bytes(b"fake image")
            files.append(str(file))
        
        output_dir = tmp_path / "output"
        
        async def mock_vectorize_with_error(input_path, output_path, callback=None):
            raise ValueError("Simulated error")
        
        with patch.object(vectorizer, 'vectorize_async', mock_vectorize_with_error):
            with pytest.raises(ValueError, match="Simulated error"):
                vectorizer.vectorize_batch(
                    input_paths=files,
                    output_dir=str(output_dir),
                    continue_on_error=False,
                )


class TestBatchParallel:
    """Tests de procesamiento paralelo."""
    
    def test_batch_parallel_mode(self, vectorizer, mock_vectorize_async, tmp_path):
        """Test: Modo paralelo procesa correctamente."""
        files = []
        for i in range(5):
            file = tmp_path / f"test{i}.png"
            file.write_bytes(b"fake image")
            files.append(str(file))
        
        output_dir = tmp_path / "output"
        
        with patch.object(vectorizer, 'vectorize_async', mock_vectorize_async):
            result = vectorizer.vectorize_batch(
                input_paths=files,
                output_dir=str(output_dir),
                parallel=True,
                max_workers=3,
            )
        
        assert result.total == 5
        assert result.successful == 5
        assert result.metadata['parallel'] is True
        assert result.metadata['max_workers'] == 3
    
    def test_batch_sequential_mode(self, vectorizer, mock_vectorize_async, tmp_path):
        """Test: Modo secuencial procesa correctamente."""
        files = []
        for i in range(3):
            file = tmp_path / f"test{i}.png"
            file.write_bytes(b"fake image")
            files.append(str(file))
        
        output_dir = tmp_path / "output"
        
        with patch.object(vectorizer, 'vectorize_async', mock_vectorize_async):
            result = vectorizer.vectorize_batch(
                input_paths=files,
                output_dir=str(output_dir),
                parallel=False,
            )
        
        assert result.total == 3
        assert result.successful == 3
        assert result.metadata['parallel'] is False


class TestBatchResults:
    """Tests de resultados del modo batch."""
    
    def test_batch_result_structure(self, vectorizer, mock_vectorize_async, tmp_path):
        """Test: Estructura del resultado batch."""
        input_file = tmp_path / "test.png"
        input_file.write_bytes(b"fake image")
        output_dir = tmp_path / "output"
        
        with patch.object(vectorizer, 'vectorize_async', mock_vectorize_async):
            result = vectorizer.vectorize_batch(
                input_paths=[str(input_file)],
                output_dir=str(output_dir),
            )
        
        assert hasattr(result, 'total')
        assert hasattr(result, 'successful')
        assert hasattr(result, 'failed')
        assert hasattr(result, 'results')
        assert hasattr(result, 'errors')
        assert hasattr(result, 'metadata')
        
        assert 'elapsed_time' in result.metadata
        assert 'parallel' in result.metadata
        assert 'output_dir' in result.metadata
    
    def test_batch_individual_results(self, vectorizer, mock_vectorize_async, tmp_path):
        """Test: Resultados individuales contienen información correcta."""
        input_file = tmp_path / "test.png"
        input_file.write_bytes(b"fake image")
        output_dir = tmp_path / "output"
        
        with patch.object(vectorizer, 'vectorize_async', mock_vectorize_async):
            result = vectorizer.vectorize_batch(
                input_paths=[str(input_file)],
                output_dir=str(output_dir),
            )
        
        assert len(result.results) == 1
        individual = result.results[0]
        
        assert individual['success'] is True
        assert 'input' in individual
        assert 'output' in individual
        assert 'filename' in individual
        assert 'quality' in individual
        assert 'iterations' in individual
        assert 'metrics' in individual
        
        assert individual['filename'] == 'test.png'
        assert individual['quality'] == 0.85
        assert individual['iterations'] == 2


class TestBatchMetadata:
    """Tests de metadata en modo batch."""
    
    def test_batch_metadata_timing(self, vectorizer, mock_vectorize_async, tmp_path):
        """Test: Metadata incluye tiempo de ejecución."""
        input_file = tmp_path / "test.png"
        input_file.write_bytes(b"fake image")
        output_dir = tmp_path / "output"
        
        with patch.object(vectorizer, 'vectorize_async', mock_vectorize_async):
            result = vectorizer.vectorize_batch(
                input_paths=[str(input_file)],
                output_dir=str(output_dir),
            )
        
        assert 'elapsed_time' in result.metadata
        assert result.metadata['elapsed_time'] >= 0
    
    def test_batch_metadata_output_dir(self, vectorizer, mock_vectorize_async, tmp_path):
        """Test: Metadata incluye directorio de salida."""
        input_file = tmp_path / "test.png"
        input_file.write_bytes(b"fake image")
        output_dir = tmp_path / "output"
        
        with patch.object(vectorizer, 'vectorize_async', mock_vectorize_async):
            result = vectorizer.vectorize_batch(
                input_paths=[str(input_file)],
                output_dir=str(output_dir),
            )
        
        assert 'output_dir' in result.metadata
        assert str(output_dir) in result.metadata['output_dir']
