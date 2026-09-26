#!/bin/sh
# Ctrl+Super+M: lee en voz alta el texto seleccionado (Piper, voz en_US-lessac-medium)
DIR=$(dirname "$(readlink -f "$0")")
PIPER=$(command -v piper || echo "$HOME/.local/bin/piper")
text=$(wl-paste --primary --no-newline 2>/dev/null)
[ -z "$text" ] && exit 0
pkill -f "paplay --raw --rate=22050" # corta la lectura anterior si la había
printf '%s' "$text" \
  | "$PIPER" -m "$DIR/voices/en_US-lessac-medium.onnx" --output-raw 2>/dev/null \
  | paplay --raw --rate=22050 --format=s16le --channels=1
