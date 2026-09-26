"""Construye dict.db (inglés → español) desde el volcado de Wiktionary de kaikki.org, en streaming.

URL=https://kaikki.org/dictionary/English/kaikki.org-dictionary-English.jsonl
curl -sL "$URL" | python build_dict.py "$(curl -sI "$URL" | grep -i content-length | tr -dc 0-9)"

Todo o nada: si los bytes recibidos no coinciden con el tamaño esperado, no toca dict.db.
Guarda: palabras con traducción al español + verbos, phrasal verbs y expresiones.
"""
import json
import os
import sqlite3
import sys
from pathlib import Path

KEEP_WITHOUT_ES = {"verb", "phrase", "prep_phrase", "adj", "adv", "intj", "proverb"}
expected = int(sys.argv[1])
final = Path(__file__).with_name("dict.db")
tmp = final.with_suffix(".tmp")
tmp.unlink(missing_ok=True)

db = sqlite3.connect(tmp)
db.execute("CREATE TABLE entries (word TEXT, pos TEXT, es TEXT, en TEXT)")

received, rows = 0, []
for raw in sys.stdin.buffer:
    received += len(raw)
    e = json.loads(raw)
    word, pos = e.get("word", ""), e.get("pos", "")
    if pos == "name":
        continue
    translations = e.get("translations", []) + [
        t for s in e.get("senses", []) for t in s.get("translations", [])]
    es = list(dict.fromkeys(t["word"] for t in translations
                            if t.get("lang_code") == "es" and t.get("word")))[:4]
    if not es and pos not in KEEP_WITHOUT_ES:
        continue
    gloss = next((s["glosses"][0] for s in e.get("senses", [])
                  if s.get("glosses") and "form-of" not in s.get("tags", [])), "")
    if not es and not gloss:
        continue
    rows.append((word.lower(), pos, ", ".join(es), gloss[:160]))
    if len(rows) >= 5000:
        db.executemany("INSERT INTO entries VALUES (?,?,?,?)", rows)
        rows.clear()

if received != expected:
    db.close()
    tmp.unlink()
    sys.exit(f"Descarga incompleta: {received} de {expected} bytes. dict.db sin tocar.")

db.executemany("INSERT INTO entries VALUES (?,?,?,?)", rows)
db.execute("CREATE INDEX idx_word ON entries(word)")
db.commit()
db.execute("VACUUM")
n = db.execute("SELECT count(*) FROM entries").fetchone()[0]
db.close()
os.replace(tmp, final)
print(n, "entradas,", final.stat().st_size // 2**20, "MB")
