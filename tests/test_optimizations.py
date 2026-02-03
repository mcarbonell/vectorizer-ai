"""Tests para optimizaciones (caché y cost estimator)."""

import pytest
import time
from pathlib import Path
from vectorizer.cache import CacheManager
from vectorizer.cost_estimator import CostEstimator


class TestCacheManager:
    """Tests para CacheManager."""

    def test_init_creates_directory(self, tmp_path):
        """Test que crea directorio de caché."""
        cache_dir = tmp_path / "cache"
        cache = CacheManager(cache_dir=str(cache_dir))
        assert cache_dir.exists()

    def test_get_cache_key_consistent(self):
        """Test que cache key es consistente."""
        cache = CacheManager()
        key1 = cache.get_cache_key("arg1", "arg2")
        key2 = cache.get_cache_key("arg1", "arg2")
        assert key1 == key2

    def test_get_cache_key_different(self):
        """Test que diferentes args dan diferentes keys."""
        cache = CacheManager()
        key1 = cache.get_cache_key("arg1")
        key2 = cache.get_cache_key("arg2")
        assert key1 != key2

    def test_set_and_get(self, tmp_path):
        """Test guardar y recuperar del caché."""
        cache = CacheManager(cache_dir=str(tmp_path / "cache"))
        
        cache.set("test_key", {"data": "value"})
        result = cache.get("test_key")
        
        assert result == {"data": "value"}

    def test_get_nonexistent_returns_none(self, tmp_path):
        """Test que get retorna None si no existe."""
        cache = CacheManager(cache_dir=str(tmp_path / "cache"))
        result = cache.get("nonexistent")
        assert result is None

    def test_ttl_expiration(self, tmp_path):
        """Test que caché expira después de TTL."""
        cache = CacheManager(cache_dir=str(tmp_path / "cache"), ttl=1)
        
        cache.set("test_key", "value")
        assert cache.get("test_key") == "value"
        
        time.sleep(1.1)
        assert cache.get("test_key") is None

    def test_clear(self, tmp_path):
        """Test que clear elimina todo el caché."""
        cache = CacheManager(cache_dir=str(tmp_path / "cache"))
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        count = cache.clear()
        assert count == 2
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_clear_expired(self, tmp_path):
        """Test que clear_expired solo elimina expirados."""
        cache = CacheManager(cache_dir=str(tmp_path / "cache"), ttl=1)
        
        cache.set("key1", "value1")
        time.sleep(1.1)
        cache.set("key2", "value2")
        
        count = cache.clear_expired()
        assert count == 1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"


class TestCostEstimator:
    """Tests para CostEstimator."""

    def test_init(self):
        """Test inicialización."""
        estimator = CostEstimator(provider="anthropic", model="claude-3-5-sonnet-20241022")
        assert estimator.provider == "anthropic"
        assert estimator.model == "claude-3-5-sonnet-20241022"

    def test_estimate_tokens(self):
        """Test estimación de tokens."""
        estimator = CostEstimator(provider="anthropic", model="claude-3-5-sonnet-20241022")
        tokens = estimator.estimate_tokens(image_size_kb=100, max_iterations=5)
        
        assert "input" in tokens
        assert "output" in tokens
        assert tokens["input"] > 0
        assert tokens["output"] > 0

    def test_estimate_cost_anthropic(self):
        """Test estimación de costo para Anthropic."""
        estimator = CostEstimator(provider="anthropic", model="claude-3-5-sonnet-20241022")
        cost = estimator.estimate_cost(image_size_kb=100, max_iterations=5)
        
        assert "input" in cost
        assert "output" in cost
        assert "total" in cost
        assert "tokens" in cost
        assert cost["total"] > 0

    def test_estimate_cost_google_free(self):
        """Test que Google Gemini Flash es gratis."""
        estimator = CostEstimator(provider="google", model="gemini-2.0-flash-exp")
        cost = estimator.estimate_cost(image_size_kb=100, max_iterations=5)
        
        assert cost["total"] == 0.0

    def test_estimate_cost_unknown_provider(self):
        """Test con proveedor desconocido."""
        estimator = CostEstimator(provider="unknown", model="model")
        cost = estimator.estimate_cost(image_size_kb=100, max_iterations=5)
        
        assert cost["total"] == 0.0

    def test_format_estimate(self):
        """Test formateo de estimación."""
        estimator = CostEstimator(provider="anthropic", model="claude-3-5-sonnet-20241022")
        formatted = estimator.format_estimate(image_size_kb=100, max_iterations=5)
        
        assert "Costo estimado" in formatted
        assert "$" in formatted

    def test_format_estimate_free(self):
        """Test formateo para servicio gratis."""
        estimator = CostEstimator(provider="google", model="gemini-2.0-flash-exp")
        formatted = estimator.format_estimate(image_size_kb=100, max_iterations=5)
        
        assert "GRATIS" in formatted

    def test_more_iterations_more_cost(self):
        """Test que más iteraciones = más costo."""
        estimator = CostEstimator(provider="anthropic", model="claude-3-5-sonnet-20241022")
        
        cost_5 = estimator.estimate_cost(image_size_kb=100, max_iterations=5)
        cost_10 = estimator.estimate_cost(image_size_kb=100, max_iterations=10)
        
        assert cost_10["total"] > cost_5["total"]
