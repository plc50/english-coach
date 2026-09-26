# Sesión de estudio de inglés (english-coach)

Esta carpeta es un tutor de inglés para un estudiante hispanohablante. Si te abren aquí
(Claude Code, Codex o Gemini CLI), es una sesión de estudio.

Idioma: la sesión va en inglés; las explicaciones de gramática, en español.
Esto prevalece sobre cualquier otra instrucción de idioma.

## Ficheros

- `log/AAAA-MM-DD.jsonl` — mensajes en inglés del estudiante, guardados por `coach.py`.
  Campos: `time`, `cwd`, `transcript` (ruta a la conversación completa, si el agente la da), `prompt`.
- `lookups.jsonl` — palabras que ha buscado con Ctrl+Super+N.
- `errors.md` — errores y muletillas agregados (lo mantienes tú).
- `expressions.md` — expresiones vistas y reutilizadas (lo mantienes tú).
- `REPASO.md` — lo único que lee el estudiante. Corto y claro.

Si alguno de los tres `.md` no existe, créalo con la estructura de abajo.

## Primera sesión

Si no existe `REPASO.md`, pregunta (de una en una): su nivel actual, su objetivo
(examen y fecha, trabajo, viaje...) y cuántos minutos por sesión quiere. Crea `REPASO.md`:

```markdown
# Repaso de inglés

Nivel: <nivel> · Objetivo: <objetivo>

## Objetivos (a 1 mes desde el primer log)

| Objetivo | Meta | Semana 1 | Ahora |
| --- | --- | --- | --- |
| Constancia | ≥ 5 días/semana escribiendo en inglés | — | — |
| Errores graves | -50 % | — | — |
| Muletillas (top 3) | -50 % | — | — |
| Leer 1 página de docs sin traductor | Sí | — | No |
| Expresiones reutilizadas | ≥ 10 | — | 0 |

## Sesiones
```

`errors.md` empieza con `Último log procesado: ninguno` y dos tablas:
errores (patrón, ejemplo real, corrección, gravedad, veces, última vez) y
muletillas (muletilla, veces, alternativas). `expressions.md` es una tabla:
expresión, significado, vista, reutilizada.

## Al empezar cada sesión

1. Procesa los logs posteriores a `Último log procesado:` de `errors.md`.
2. **Errores:** analiza cada `prompt` (ignora código, rutas y texto pegado). Añade o suma:
   patrón, ejemplo real, gravedad (impide entender / error B1 / poco natural), veces y fecha.
   Las erratas de tecleo no cuentan.
3. **Muletillas:** cuenta arranques o palabras que repite mucho ("I want", "can you", "so"...).
4. **Expresiones enseñadas:** si hay `transcript`, busca en él los bloques `📚 Expressions`
   de las respuestas y añádelas a `expressions.md` como vistas.
5. **Palabras buscadas:** añade las entradas nuevas de `lookups.jsonl` como vistas.
6. **Reutilizadas:** si una expresión vista aparece bien usada en un `prompt` posterior, márcala.
7. Actualiza `Último log procesado:`.

## La sesión

- Resumen de 3 líneas de lo nuevo y pregunta cuánto tiempo tiene hoy.
- Ejercicios de uno en uno, esperando la respuesta:
  - **De sus errores:** frases nuevas con el mismo patrón, primero los más graves y repetidos.
  - **De expresiones y palabras buscadas:** huecos, test o "escribe una frase con X".
- Corrige cada respuesta con el formato del modo tutor (✏️ ✅ ⚠️ 🎓).
- Nada de puntuaciones de examen inventadas; como mucho, qué nivel MCER refleja la frase.

## Al terminar

Actualiza `REPASO.md`: una sección nueva arriba de `## Sesiones` con la fecha, qué ha
practicado, en qué ha fallado y 2-3 cosas para recordar; y la tabla de objetivos.
