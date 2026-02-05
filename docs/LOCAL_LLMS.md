# LLMs Locales (Ollama y LM Studio)

Este documento describe cómo usar LLMs locales con Vectorizer AI mediante Ollama o LM Studio.

## Requisitos previos

### Ollama

1. Instalar Ollama desde [ollama.com](https://ollama.com)
2. Iniciar el servicio: `ollama serve`
3. Descargar un modelo con visión:
   ```bash
   # Modelo recomendado para visión
   ollama pull llama3.2-vision

   # Alternativa más ligera
   ollama pull llava
   ```

### LM Studio

1. Descargar LM Studio desde [lmstudio.ai](https://lmstudio.ai)
2. Descargar un modelo con visión (formato GGUF)
3. Iniciar el servidor local (通常 en `http://localhost:1234`)

## Modelos recomendados

| Modelo | Proveedor | Memoria RAM | Visión |
|--------|-----------|-------------|--------|
| llama3.2-vision | Ollama | ~8GB | ✓ |
| llava | Ollama | ~4GB | ✓ |
| llama3.2-vision | LM Studio | ~8GB | ✓ |

## Uso desde CLI

### Ollama

```bash
# Usar Ollama con modelo por defecto (llava)
vectorizer imagen.png salida.svg --provider ollama

# Especificar modelo diferente
vectorizer imagen.png salida.svg --provider ollama --model llama3.2-vision

# Con URL personalizada
vectorizer imagen.png salida.svg --provider ollama --base-url http://localhost:11434/v1
```

### LM Studio

```bash
# Usar LM Studio
vectorizer imagen.png salida.svg --provider lmstudio

# Especificar modelo
vectorizer imagen.png salida.svg --provider lmstudio --model mi-modelo-gguf
```

## Uso desde Python

```python
from vectorizer import Vectorizer

# Usar Ollama
vectorizer = Vectorizer(
    api_key="not-needed",  # No requiere API key
    model="llama3.2-vision",
    provider="ollama"
)

# Usar LM Studio
vectorizer = Vectorizer(
    api_key="not-needed",
    model="mi-modelo",
    provider="lmstudio",
    base_url="http://localhost:1234/v1"
)

# Vectorizar imagen
result = vectorizer.vectorize("imagen.png", "salida.svg")
print(f"Calidad: {result.quality}")
```

## Verificar conexión

### CLI

```bash
# Probar conexión con Ollama
curl http://localhost:11434/api/tags

# Probar conexión con LM Studio
curl http://localhost:1234/v1/models
```

### Python

```python
from vectorizer.local_llm import create_local_client

# Crear cliente Ollama
client = create_local_client("ollama", model="llava")

# Probar conexión
if client.test_connection():
    print("✓ Conexión exitosa")
else:
    print("✗ Error de conexión")

# Listar modelos disponibles
models = client.list_models()
print(f"Modelos disponibles: {models}")
```

## Notas importantes

1. **Sin API key**: Los LLMs locales no requieren API key, usa `api_key="not-needed"`
2. **Recursos**: Los modelos con visión requieren más RAM (4-8GB mínimo)
3. **Primera ejecución**: La primera vez puede ser lenta mientras el modelo carga
4. **Puerto por defecto**:
   - Ollama: `http://localhost:11434/v1`
   - LM Studio: `http://localhost:1234/v1`

## Solución de problemas

### Error: "Proveedor no soportado"
Asegúrate de usar `--provider ollama` o `--provider lmstudio` (no "local")

### Error: "Conexión rechazada"
- Verifica que el servidor esté ejecutándose
- Comprueba el puerto (11434 para Ollama, 1234 para LM Studio)
- Revisa el firewall

### Error: "Modelo no encontrado"
- Verifica que el modelo esté descargado: `ollama list` o en LM Studio
- Asegúrate de que el nombre del modelo sea correcto
