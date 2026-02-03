"""Biblioteca de prompts mejorados con ejemplos few-shot."""

# Ejemplos few-shot para análisis de imágenes
ANALYSIS_EXAMPLES = """
Ejemplo 1:
Imagen: Logo con texto "ACME" en azul y una estrella amarilla
Análisis:
{
    "shapes": ["text", "star", "rectangle"],
    "colors": ["#0066CC", "#FFD700"],
    "composition": "centered",
    "complexity": "simple",
    "style": "flat",
    "description": "Logo corporativo con texto ACME en azul y estrella amarilla"
}

Ejemplo 2:
Imagen: Icono de corazón rojo con sombra
Análisis:
{
    "shapes": ["heart", "shadow"],
    "colors": ["#FF0000", "#00000033"],
    "composition": "centered",
    "complexity": "simple",
    "style": "flat con sombra",
    "description": "Icono de corazón rojo con efecto de sombra sutil"
}
"""

# Ejemplos few-shot para generación de SVG
SVG_GENERATION_EXAMPLES = """
Ejemplo 1:
Descripción: Círculo rojo centrado
SVG:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#FF0000"/>
</svg>

Ejemplo 2:
Descripción: Texto "Hello" en azul
SVG:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">
  <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" 
        font-family="Arial" font-size="24" fill="#0066CC">Hello</text>
</svg>

Ejemplo 3:
Descripción: Logo con texto y forma
SVG:
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">
  <rect x="10" y="10" width="180" height="80" rx="10" fill="#F0F0F0"/>
  <text x="100" y="55" text-anchor="middle" font-family="Arial" 
        font-size="20" font-weight="bold" fill="#333">LOGO</text>
</svg>
"""


def get_analysis_prompt(description: str, colors: list, shapes: list, style: str) -> str:
    """Genera prompt mejorado para análisis con few-shot.
    
    Args:
        description: Descripción de la imagen.
        colors: Colores principales.
        shapes: Formas principales.
        style: Estilo visual.
    
    Returns:
        Prompt optimizado con ejemplos.
    """
    return f"""Analiza esta imagen y proporciona información estructurada.

{ANALYSIS_EXAMPLES}

Ahora analiza la imagen actual y responde en el mismo formato JSON.
Sé preciso con los colores (formato hexadecimal) y las formas.
"""


def get_generation_prompt(analysis: dict, style: str = "flat") -> str:
    """Genera prompt mejorado para generación de SVG con few-shot.
    
    Args:
        analysis: Análisis de la imagen.
        style: Estilo deseado.
    
    Returns:
        Prompt optimizado con ejemplos.
    """
    shapes_str = ', '.join(analysis.get('shapes', [])) if analysis.get('shapes') else 'formas básicas'
    colors_str = ', '.join(analysis.get('colors', [])) if analysis.get('colors') else 'colores apropiados'
    
    return f"""Genera un código SVG basado en el siguiente análisis:

Descripción: {analysis.get('description', 'imagen')}
Formas: {shapes_str}
Colores: {colors_str}
Composición: {analysis.get('composition', 'centrada')}
Estilo: {style}

{SVG_GENERATION_EXAMPLES}

REQUISITOS IMPORTANTES:
1. Usa SOLO los colores especificados: {colors_str}
2. El SVG debe ser válido y bien formado
3. Incluye xmlns="http://www.w3.org/2000/svg"
4. Usa viewBox para hacerlo responsive
5. Si hay texto, usa elementos <text>, NO paths
6. Mantén el código limpio y legible
7. NO incluyas comentarios en el SVG
8. Devuelve SOLO el código SVG, sin explicaciones

Genera el SVG ahora:"""


def get_modification_prompt(svg_code: str, modifications: list, context: dict = None) -> str:
    """Genera prompt mejorado para modificación de SVG.
    
    Args:
        svg_code: Código SVG actual.
        modifications: Lista de modificaciones a aplicar.
        context: Contexto de iteraciones anteriores.
    
    Returns:
        Prompt optimizado.
    """
    mods_text = '\n'.join(f"- {mod}" for mod in modifications)
    
    context_text = ""
    if context and context.get('previous_attempts'):
        context_text = f"\n\nINTENTOS PREVIOS (evita repetir estos errores):\n"
        for attempt in context['previous_attempts'][-2:]:  # Últimos 2 intentos
            context_text += f"- {attempt}\n"
    
    return f"""Modifica el siguiente código SVG aplicando estos cambios específicos:

{mods_text}
{context_text}

SVG ACTUAL:
{svg_code}

INSTRUCCIONES:
1. Aplica SOLO las modificaciones solicitadas
2. Mantén el resto del SVG sin cambios
3. El SVG resultante debe ser válido
4. Preserva la estructura y estilo existente
5. Si hay texto, manténlo como <text>, no lo conviertas a paths
6. Devuelve SOLO el código SVG modificado, sin explicaciones

SVG modificado:"""
