"""Traducción + significado de un texto, offline y sin tokens.

dict.db (Wiktionary): palabras, phrasal verbs y expresiones con traducción humana.
Solo stdlib: python3 lookup.py "got the hang of"   |   --test
"""
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).with_name("dict.db")
# Verbos irregulares más comunes (las formas regulares las resuelve base_forms)
IRREGULAR = {}
for base, *forms in (v.split("/") for v in """
be/was/were/been/is/are/am become/became beat/beaten begin/began/begun bend/bent bite/bit/bitten
blow/blew/blown break/broke/broken bring/brought build/built burn/burnt buy/bought catch/caught
choose/chose/chosen come/came cost/costs cut/cuts deal/dealt dig/dug do/did/done/does draw/drew/drawn
dream/dreamt drink/drank/drunk drive/drove/driven eat/ate/eaten fall/fell/fallen feed/fed feel/felt
fight/fought find/found fly/flew/flown forget/forgot/forgotten forgive/forgave/forgiven freeze/froze/frozen
get/got/gotten give/gave/given go/went/gone/goes grow/grew/grown hang/hung have/had/has hear/heard
hide/hid/hidden hit/hits hold/held hurt/hurts keep/kept know/knew/known lay/laid lead/led lean/leant
learn/learnt leave/left lend/lent let/lets lie/lay/lain light/lit lose/lost make/made mean/meant
meet/met pay/paid put/puts quit/quits read/reads ride/rode/ridden ring/rang/rung rise/rose/risen
run/ran say/said see/saw/seen seek/sought sell/sold send/sent set/sets shake/shook/shaken shine/shone
shoot/shot show/shown shut/shuts sing/sang/sung sink/sank/sunk sit/sat sleep/slept slide/slid
speak/spoke/spoken spend/spent spin/spun split/splits spread/spreads stand/stood steal/stole/stolen
stick/stuck sting/stung strike/struck swear/swore/sworn sweep/swept swim/swam/swum swing/swung
take/took/taken teach/taught tear/tore/torn tell/told think/thought throw/threw/thrown
understand/understood wake/woke/woken wear/wore/worn win/won write/wrote/written
""".split()):
    for f in forms:
        IRREGULAR[f] = base


def base_forms(w):
    """Posibles formas base de una palabra regular: pushed → push, stopping → stop, tries → try."""
    forms = [w, IRREGULAR.get(w, w)]
    for suf, reps in (("ies", ["y"]), ("ied", ["y"]), ("es", ["", "e"]), ("s", [""]),
                      ("ed", ["", "e"]), ("ing", ["", "e"])):
        if w.endswith(suf) and len(w) >= len(suf) + 2:
            stem = w[: -len(suf)]
            forms += [stem + r for r in reps]
            if len(stem) > 2 and stem[-1] == stem[-2]:  # stopped → stop
                forms.append(stem[:-1])
    return list(dict.fromkeys(forms))


def candidates(text):
    """Texto tal cual, con la 1.ª palabra en forma base (pushed back → push back) y sin la última."""
    words = text.lower().strip(" .,;:!?\"'()").split()
    if not words:
        return []
    bases = base_forms(words[0])
    out = [" ".join([b, *words[1:]]) for b in bases]
    if len(words) > 2:  # run out of → run out
        out += [" ".join([b, *words[1:-1]]) for b in bases]
    return list(dict.fromkeys(out))


def from_dict(text):
    """Primera forma candidata con traducción al español; si ninguna tiene, la primera que exista."""
    if not DB.exists():
        return None
    db = sqlite3.connect(DB)
    found = []
    for c in candidates(text):
        rows = db.execute("SELECT es, en FROM entries WHERE word = ?", (c,)).fetchall()
        if rows:
            es = next((r[0] for r in rows if r[0]), "")
            en = next((r[1] for r in rows if r[1]), "")
            found.append((c, ", ".join(es.split(", ")[:3]), en))
    return next((f for f in found if f[1]), found[0] if found else None)


def lookup(text):
    text = " ".join(text.split())
    hit = from_dict(text) if len(text.split()) <= 5 else None
    if not hit:
        return "No está en el diccionario"
    word, es, en = hit
    lines = ([f"ES: {es}"] if es else []) + ([f"EN: {en}"] if en else [])
    if word != candidates(text)[0]:
        lines.insert(0, f"→ {word}")
    return "\n".join(lines)


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        assert "push back" in candidates("pushed back")
        assert "get the hang of" in candidates("got the hang of")
        assert "run out" in candidates("ran out of")
        assert "tranquillo" in lookup("got the hang of")
        assert lookup("stopped").startswith("→ stop")
        assert "stop" in base_forms("stopping") and "try" in base_forms("tries")
        assert lookup("I would like to learn English this year") == "No está en el diccionario"
        print("ok")
    else:
        print(lookup(" ".join(sys.argv[1:])))
