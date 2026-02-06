"""Sistema de caché para Vectorizer AI."""

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """Gestor de caché para respuestas de API."""

    def __init__(self, cache_dir: str = ".cache", ttl: int = 3600):
        """Inicializa el CacheManager.

        Args:
            cache_dir: Directorio para archivos de caché.
            ttl: Tiempo de vida del caché en segundos (default: 1 hora).
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Cache inicializado en {self.cache_dir} con TTL={ttl}s")

    def get_cache_key(self, *args: Any) -> str:
        """Genera clave de caché basada en argumentos.

        Args:
            *args: Argumentos para generar la clave.

        Returns:
            Hash MD5 como clave de caché.
        """
        # Convertir args a string y hashear
        key_str = json.dumps(args, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del caché.

        Args:
            key: Clave de caché.

        Returns:
            Valor cacheado o None si no existe o expiró.
        """
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            logger.debug(f"Cache miss: {key}")
            return None

        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))

            # Verificar TTL
            if time.time() - data["timestamp"] > self.ttl:
                logger.debug(f"Cache expired: {key}")
                cache_file.unlink(missing_ok=True)
                return None

            logger.debug(f"Cache hit: {key}")
            return data["value"]
        except Exception as e:
            logger.warning(f"Error leyendo caché: {e}")
            return None

    def set(self, key: str, value: Any) -> None:
        """Guarda valor en caché.

        Args:
            key: Clave de caché.
            value: Valor a cachear.
        """
        cache_file = self.cache_dir / f"{key}.json"

        try:
            data = {"timestamp": time.time(), "value": value}
            cache_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            logger.debug(f"Cache saved: {key}")
        except Exception as e:
            logger.warning(f"Error guardando caché: {e}")

    def clear(self) -> int:
        """Limpia todo el caché.

        Returns:
            Número de archivos eliminados.
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        logger.info(f"Cache cleared: {count} files")
        return count

    def clear_expired(self) -> int:
        """Limpia caché expirado.

        Returns:
            Número de archivos eliminados.
        """
        count = 0
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                if current_time - data["timestamp"] > self.ttl:
                    cache_file.unlink()
                    count += 1
            except Exception:
                # Si hay error, eliminar archivo corrupto
                cache_file.unlink()
                count += 1

        if count > 0:
            logger.info(f"Expired cache cleared: {count} files")
        return count
