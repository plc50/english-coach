#!/usr/bin/env bash
# Quita los hooks y los atajos de english-coach. No borra tus datos de study/.
set -euo pipefail

DIR=$(cd "$(dirname "$0")" && pwd)
CMD="python3 $DIR/coach.py"

for pair in "$HOME/.claude/settings.json:UserPromptSubmit" "$HOME/.codex/hooks.json:UserPromptSubmit" \
            "$HOME/.gemini/settings.json:BeforeAgent"; do
  file=${pair%%:*} ev=${pair##*:}
  [[ -s $file ]] || continue
  tmp=$(mktemp)  # temporal + mv: si jq falla, el fichero original queda intacto
  if jq --arg ev "$ev" --arg cmd "$CMD" '
       if .hooks[$ev] then .hooks[$ev] |= map(select([.hooks[]?.command] | index($cmd) | not)) else . end
     ' "$file" >"$tmp" 2>/dev/null; then
    cp "$file" "$file.bak" && mv "$tmp" "$file"
    echo "✓ hook quitado de $file"
  else
    rm -f "$tmp"
    echo "! no puedo leer $file como JSON: quita a mano el hook \"$CMD\""
  fi
done

for cfg in "$HOME/.config/hypr/hyprland.lua" "$HOME/.config/hypr/hyprland.conf"; do
  [[ -f $cfg ]] && grep -q '>>> english-coach' "$cfg" || continue
  sed -i.bak '/>>> english-coach >>>/,/<<< english-coach <<</d' "$cfg"
  echo "✓ atajos quitados de $cfg"
done
command -v hyprctl >/dev/null && hyprctl reload >/dev/null || true

echo "Para borrarlo todo: rm -rf $DIR  (y uv tool uninstall piper-tts si no lo usas para otra cosa)"
