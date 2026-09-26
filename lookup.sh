#!/bin/sh
# Ctrl+Super+N: traducción + significado del texto seleccionado (offline, sin tokens).
# Cada búsqueda se guarda en study/lookups.jsonl para la sesión de estudio.
DIR=$(dirname "$(readlink -f "$0")")
text=$(wl-paste --primary --no-newline 2>/dev/null)
[ -z "$text" ] && exit 0
result=$(python3 "$DIR/lookup.py" "$text" 2>/dev/null)
# el cuerpo de la notificación se interpreta como marcado: escapa & < >
esc() { printf '%s' "$1" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g'; }
notify-send -t 15000 -- "$(esc "$text")" "$(esc "$result")"
jq -cn --arg t "$text" --arg r "$result" '{time: (now | todate), text: $t, result: $r}' \
  >> "$DIR/study/lookups.jsonl"
