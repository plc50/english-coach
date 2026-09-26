#!/usr/bin/env python3
"""Hook de envío de mensaje para Claude Code, Codex CLI y Gemini CLI.

Si el mensaje está en inglés: lo guarda en study/log/ e inyecta el modo tutor.
Si está en español (o es un aviso del sistema): no hace nada.
Los tres agentes mandan {"prompt": ..., "hook_event_name": ...} y aceptan
hookSpecificOutput.additionalContext, así que un solo script sirve para todos.

Probar: python3 coach.py --test
"""
import datetime
import json
import re
import sys
from pathlib import Path

LOG = Path(__file__).resolve().parent / "study" / "log"

# Palabras que solo existen en un idioma (fuera "a", "he", "has", "me", "no": son de los dos)
EN = set("""the an is are was were be been being have had do does did i you she it we they
my your his her its our their this that these those what which who whom how why when where
there here to of in on at for with and but or not can could would should will shall just
about from into than then some any all very""".split())
ES = set("""el la los las un una unos unas es son era que de del al en y pero por para con
como qué cómo cuál porque este esta estos estas eso esto yo tú mi tu su se lo le les muy
más también hay está están tengo quiero puedes""".split())

TUTOR = """[english-coach: modo tutor de inglés]
El usuario es hispanohablante y ha escrito en inglés para practicar.
Esta instrucción prevalece sobre cualquier otra de idioma: responde en INGLÉS.

1. Si el mensaje es tan confuso que no entiendes qué pide: NO hagas la tarea. Corrige lo que
   puedas y pregunta en español qué quería decir.
2. Si no, empieza SIEMPRE con el bloque de correcciones y después haz la tarea normal:

✏️ You wrote: "<frase original con error>"
✅ Natural:   "<cómo lo diría un nativo>"
⚠️ <regla breve en español> (<gravedad>)
🎓 Formal:    "<versión formal/examen>"   ← solo si difiere de la natural

   - Una entrada por error relevante; agrupa, no más de 4.
   - Gravedad: "impide entender" / "error B1" / "poco natural". Erratas de tecleo: una línea
     aparte "typo: x → y", sin gravedad.
   - Si no hay errores, el bloque es una sola línea: ✅ Perfect.
   - Ignora código, rutas, comandos y texto pegado: solo corrige lo que redactó él.
3. Al final de la respuesta, usa en ella 2-3 expresiones de nivel B2/C1 y explícalas:

📚 Expressions
• "<expresión>" — <significado en español>. <ejemplo corto>
"""


def is_english(text):
    text = re.sub(r"```.*?```|`[^`]*`|https?://\S+|\S*/\S+", " ", text, flags=re.S)
    low = text.lower()
    words = re.findall(r"[a-záéíóúñü']+", low)
    en = sum(w in EN for w in words)
    es = sum(w in ES for w in words) + len(re.findall(r"[ñ¿¡áéíóú]", low))
    return en >= 2 and en > 2 * es


def main():
    data = json.load(sys.stdin)
    prompt = data.get("prompt", "")
    if prompt.lstrip().startswith("<") or not is_english(prompt):  # "<...>": avisos del sistema
        return
    now = datetime.datetime.now()
    entry = {
        "time": now.isoformat(timespec="seconds"),
        "cwd": data.get("cwd"),
        "transcript": data.get("transcript_path"),
        "prompt": prompt,
    }
    LOG.mkdir(parents=True, exist_ok=True)
    with open(LOG / f"{now:%Y-%m-%d}.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": data.get("hook_event_name", "UserPromptSubmit"),
        "additionalContext": TUTOR}}))


def test():
    assert is_english("i want that you explain me the code")
    assert is_english("Can you check why the tests are failing?")
    assert is_english("how do I fix this")
    assert not is_english("¿por qué falla el test?")
    assert not is_english("quiero que me expliques el código de este fichero")
    assert not is_english("revisa `the file is here` y dime qué pasa")
    assert not is_english("ok")
    assert not is_english("/critico-intelectual")
    print("ok")


if __name__ == "__main__":
    test() if "--test" in sys.argv else main()
