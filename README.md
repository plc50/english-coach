# english-coach

**Aprende inglés sin sacar tiempo extra: tu agente de IA te corrige mientras trabajas.**

Lo hice para mejorar mi propio inglés. Paso muchas horas escribiendo a agentes de IA en la
terminal, así que esas horas ya cuentan como práctica. Te corrige al momento, te enseña
expresiones de nivel B2/C1 y, cuando te apetece, te prepara una sesión de estudio con tus
propios errores. Si quieres integrar el inglés en tu día a día de forma pasiva, es tuyo.

```
> i want that you explain me the code

✏️ You wrote: "i want that you explain me the code"
✅ Natural:   "I want you to explain the code to me"
⚠️ want + that → want + alguien + to (error B1)

[...la respuesta normal a tu pregunta...]

📚 Expressions
• "to get the hang of sth" — pillarle el truco. I'm getting the hang of hooks.
```

## Qué hace

| | Cuándo | Coste |
|---|---|---|
| **Tutor pasivo** | Escribes en inglés a Claude Code, Codex o Gemini CLI → te corrige antes de responder y te enseña 2-3 expresiones B2/C1 | Solo se activa en inglés. En español no hace nada |
| **Traducir** `Ctrl+Super+N` | Seleccionas una palabra o *phrasal verb* en cualquier ventana → notificación con traducción y significado | Offline, 0 tokens, ~0,05 s |
| **Pronunciar** `Ctrl+Super+M` | Seleccionas texto → lo lee una voz neuronal | Offline, 0 tokens |
| **Sesión de estudio** | Cuando tú quieras: ejercicios hechos con **tus** errores y **tus** palabras buscadas | Lo que dure la sesión |

Todo se guarda en local (`study/`). Nada sale de tu máquina salvo lo que ya le mandas a tu agente.

## Quick start

Necesitas Hyprland y al menos uno de: [Claude Code](https://claude.com/claude-code),
[Codex CLI](https://github.com/openai/codex) o [Gemini CLI](https://github.com/google-gemini/gemini-cli).

```bash
git clone https://github.com/plc50/english-coach.git ~/english-coach
cd ~/english-coach && ./install.sh
```

Si te falta algo, el instalador te dice qué instalar (en Arch:
`sudo pacman -S --needed python jq curl wl-clipboard libnotify libpulse uv`).

El instalador:
- detecta qué agentes tienes y añade el hook sin tocar el resto de tu configuración (deja un `.bak`);
- solo añade los atajos si `Ctrl+Super+N` y `Ctrl+Super+M` están libres; si no, te avisa y no toca nada;
- se puede ejecutar varias veces sin duplicar nada.

## Uso

1. **Día a día:** escribe a tu agente en inglés cuando no vayas con prisa. Con prisa, en español: no pasa nada.
2. **Leyendo docs:** selecciona lo que no entiendas → `Ctrl+Super+N`. ¿Cómo se pronuncia? → `Ctrl+Super+M`.
3. **Cuando te apetezca estudiar:**
   ```bash
   cd ~/english-coach/study && claude   # o codex / gemini
   ```
   La primera vez te pregunta tu nivel y tu objetivo. Después analiza tus mensajes, te pone
   ejercicios y actualiza `study/REPASO.md`, que es lo único que tienes que leer tú.

## Cómo funciona

```
tu mensaje ──► coach.py ──¿inglés?──no──► (nada)
                   │ sí
                   ├─► study/log/AAAA-MM-DD.jsonl
                   └─► instrucciones del tutor ──► tu agente responde con correcciones

Ctrl+Super+N ──► lookup.py ──► dict.db (Wiktionary, 320k entradas) ──► notificación
Ctrl+Super+M ──► say.sh ──► Piper ──► altavoces

sesión de estudio ──► lee log/ + lookups.jsonl ──► ejercicios ──► REPASO.md
```

- **Detección de idioma:** cuenta palabras que solo existen en inglés o en español. Sin
  modelos ni red, en milisegundos. Ignora código, rutas y URLs.
- **Un solo script para los tres agentes:** Claude Code y Codex (`UserPromptSubmit`) y Gemini
  CLI (`BeforeAgent`) mandan el mismo `prompt` y aceptan el mismo `additionalContext`.
- **Diccionario:** entiende formas conjugadas (*got the hang of* → *get the hang of*,
  *ran out of* → *run out*) y prefiere traducciones hechas por personas.

¿Y Cursor o Copilot CLI? Sus hooks aún no permiten inyectar contexto al enviar el mensaje
([Cursor](https://forum.cursor.com/t/hooks-allow-beforesubmitprompt-hook-to-inject-additional-context/150707),
[Copilot #2652](https://github.com/github/copilot-cli/issues/2652)). Cuando lo hagan, se añaden.

## Limitaciones

- La detección falla si pegas mucho texto en inglés con una pregunta corta en español.
- Algunas entradas de Wiktionary no tienen traducción al español (sale solo el significado en inglés).
- Si seleccionas dentro de tmux/Zellij con el ratón capturado, mantén `Shift` al seleccionar.
- Pensado para hispanohablantes: traducciones y explicaciones en español.

## Desinstalar

```bash
~/english-coach/uninstall.sh   # quita hooks y atajos; tus datos de study/ se quedan
```

## Créditos y licencias

- Código: [MIT](LICENSE).
- Diccionario: [Wiktionary](https://en.wiktionary.org) vía [kaikki.org](https://kaikki.org),
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Para regenerarlo: `build_dict.py`.
- Voz: [Piper](https://github.com/OHF-Voice/piper1-gpl) con
  [en_US-lessac-medium](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/lessac/medium)
  (revisa la licencia del dataset en su model card antes de un uso comercial).
