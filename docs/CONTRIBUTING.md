# Guía de Contribución

¡Gracias por tu interés en contribuir a Vectorizer AI! Esta guía te ayudará a empezar.

## Código de Conducta

- Ser respetuoso y considerado
- Aceptar críticas constructivas
- Enfocarse en lo que es mejor para la comunidad
- Mostrar empatía hacia otros contribuidores

## Cómo Contribuir

### Reportar Bugs

Antes de reportar un bug, por favor:

1. Busca en los issues existentes
2. Verifica que el bug aún no ha sido reportado
3. Recopila la siguiente información:
   - Versión de Python
   - Versión del paquete
   - Sistema operativo
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Logs o mensajes de error

### Sugerir Mejoras

Las sugerencias de mejora son bienvenidas. Por favor:

1. Busca en los issues existentes
2. Verifica que la sugerencia aún no ha sido propuesta
3. Proporciona una descripción clara de la mejora
4. Explica por qué sería útil
5. Considera si puedes implementarla tú mismo

### Pull Requests

#### Antes de Crear un PR

1. Lee la [Guía de Desarrollo](development.md)
2. Configura tu entorno de desarrollo
3. Crea una rama para tu PR
4. Escribe código siguiendo las convenciones
5. Escribe tests para tu código
6. Asegúrate de que todos los tests pasen
7. Actualiza la documentación si es necesario

#### Creando un PR

1. Fork el repositorio
2. Clona tu fork:
   ```bash
   git clone https://github.com/tu-usuario/vectorizer-ai.git
   cd vectorizer-ai
   ```
3. Añade el upstream:
   ```bash
   git remote add upstream https://github.com/original-owner/vectorizer-ai.git
   ```
4. Crea una rama nueva:
   ```bash
   git checkout -b feature/nombre-de-la-funcionalidad
   ```
5. Haz tus cambios y commitea:
   ```bash
   git add .
   git commit -m "feat: descripción concisa del cambio"
   ```
6. Push a tu fork:
   ```bash
   git push origin feature/nombre-de-la-funcionalidad
   ```
7. Crea un PR desde GitHub

#### Convenciones de Commit

Usa [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<alcance>): <descripción>

[opcional cuerpo]

[opcional pie de página]
```

**Tipos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (sin lógica)
- `refactor`: Refactorización de código
- `test`: Agregar o actualizar tests
- `chore`: Cambios en build/config

**Ejemplos:**
```
feat(vision): agregar soporte para modelo GPT-4V
fix(comparator): corregir cálculo de SSIM
docs(api): actualizar documentación de SVGGenerator
```

#### Plantilla de PR

```markdown
## Descripción
Breve descripción de los cambios.

## Tipo de Cambio
- [ ] Bug fix (non-breaking change que corrige un issue)
- [ ] Nueva feature (non-breaking change que agrega funcionalidad)
- [ ] Breaking change (fix o feature que causa cambios incompatibles)

## Tests
- [ ] Tests agregados/actualizados
- [ ] Todos los tests pasan

## Documentación
- [ ] README actualizado
- [ ] API docs actualizados
- [ ] CHANGELOG actualizado

## Checklist
- [ ] Mi código sigue las convenciones de estilo
- [ ] He realizado auto-revisión de mi código
- [ ] He comentado código complejo
- [ ] He actualizado la documentación
- [ ] Mis cambios no generan nuevos warnings
- [ ] He agregado tests que prueban mis cambios
- [ ] Todos los tests nuevos y existentes pasan
```

## Estándares de Código

### Python

- Seguir PEP 8
- Usar type hints
- Escribir docstrings (Google Style)
- Máximo 88 caracteres por línea
- Imports ordenados

### Tests

- Usar pytest
- Tests deben ser independientes
- Usar fixtures para configuración común
- Mockear APIs externas
- Cobertura mínima: 80%

### Documentación

- Docstrings en todas las funciones públicas
- Actualizar README para cambios importantes
- Actualizar CHANGELOG para releases
- Ejemplos de uso para nuevas features

## Proceso de Revisión

### Qué esperar

1. Revisión automática (CI/CD)
2. Revisión por mantenedores
3. Feedback y solicitudes de cambios
4. Aprobación y merge

### Tiempos de Respuesta

- Respuesta inicial: 2-3 días
- Revisión completa: 1 semana
- Merge: después de aprobación

### Feedback

- Ser constructivo y específico
- Explicar el "por qué" de los cambios
- Ofrecer sugerencias de mejora
- Reconocer buen trabajo

## Proyectos de Contribución

### Etiqueta: `good first issue`

Issues marcados con esta etiqueta son buenos para empezar:
- Pequeños cambios
- Bien definidos
- Con contexto suficiente

### Etiqueta: `help wanted`

Issues que necesitan ayuda de la comunidad:
- Features importantes
- Bugs complejos
- Mejoras de rendimiento

## Comunicación

### Canales

- GitHub Issues: Para bugs y features
- GitHub Discussions: Para preguntas y debate
- Pull Requests: Para código y documentación

### Idioma

El idioma principal del proyecto es español. Por favor:
- Usa español en issues y PRs
- Documentación en español
- Comentarios en código en español

## Reconocimiento

Los contribuidores serán reconocidos en:
- README.md
- CHANGELOG.md
- Release notes

## Licencia

Al contribuir, acuerdas que tus contribuciones serán licenciadas bajo la MIT License.

## Preguntas Frecuentes

### ¿Puedo contribuir si soy nuevo en Python?

¡Sí! Hay tareas para todos los niveles:
- Documentación
- Tests
- Issues simples
- Traducciones

### ¿Cómo puedo encontrar qué contribuir?

1. Mira issues con etiquetas `good first issue` o `help wanted`
2. Lee la documentación
3. Únete a las discusiones
4. Pregunta en un issue

### ¿Qué pasa si mi PR es rechazado?

No te desanimes:
- Pregunta por qué fue rechazado
- Aprende del feedback
- Intenta de nuevo con los cambios sugeridos

### ¿Puedo contribuir con documentación?

¡Absolutamente! La documentación es muy importante:
- Correcciones gramaticales
- Mejoras en claridad
- Nuevos ejemplos
- Traducciones

## Recursos

- [Guía de Desarrollo](development.md)
- [Arquitectura del Sistema](architecture.md)
- [API Reference](api.md)
- [Python PEP 8](https://peps.python.org/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## Contacto

Para preguntas sobre contribución:
- Abre un issue con la etiqueta `question`
- Únete a las discusiones
- Contacta a los mantenedores

---

¡Gracias por contribuir a Vectorizer AI! 🎨
