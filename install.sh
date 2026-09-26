#!/usr/bin/env bash
# english-coach: instalación en ~2-3 min. Se puede ejecutar varias veces sin duplicar nada.
set -euo pipefail

DIR=$(cd "$(dirname "$0")" && pwd)
CMD="python3 $DIR/coach.py"
DICT_URL=${DICT_URL:-https://github.com/plc50/english-coach/releases/latest/download/dict.db}
WIKT_URL=https://kaikki.org/dictionary/English/kaikki.org-dictionary-English.jsonl
VOICE_URL=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; }
step() { printf '\n\033[1m%s\033[0m\n' "$1"; }

step "1/5 Dependencias"
missing=()
for c in python3 jq curl wl-paste notify-send paplay uv; do
  command -v "$c" >/dev/null || missing+=("$c")
done
if ((${#missing[@]})); then
  echo "  Faltan: ${missing[*]}"
  echo "  En Arch: sudo pacman -S --needed python jq curl wl-clipboard libnotify libpulse uv"
  exit 1
fi
ok "todo instalado"

step "2/5 Diccionario (Wiktionary, offline)"
if [[ -s $DIR/dict.db ]]; then
  ok "ya existe"
elif curl -fsSL "$DICT_URL" -o "$DIR/dict.tmp"; then
  mv "$DIR/dict.tmp" "$DIR/dict.db" && ok "descargado ($(du -h "$DIR/dict.db" | cut -f1))"
else
  warn "no hay versión publicada: lo construyo desde Wiktionary (~5 min, 3 GB en streaming, nada se guarda salvo el diccionario)"
  # -L: el tamaño de la URL final, no el de una redirección
  size=$(curl -sIL "$WIKT_URL" | grep -i '^content-length' | tail -1 | tr -dc 0-9 || true)
  [[ -n $size ]] || { echo "  No puedo saber el tamaño del volcado de Wiktionary. Prueba más tarde."; exit 1; }
  curl -fsSL --retry 3 "$WIKT_URL" | python3 "$DIR/build_dict.py" "$size"
fi

step "3/5 Voz (Piper, offline)"
command -v piper >/dev/null || [[ -x $HOME/.local/bin/piper ]] || uv tool install -q piper-tts
mkdir -p "$DIR/voices"
for ext in onnx onnx.json; do
  f=$DIR/voices/en_US-lessac-medium.$ext
  # a .tmp y luego mv: una descarga cortada no se queda pasando por buena
  [[ -s $f ]] || { curl -fsSL "$VOICE_URL${ext#onnx}" -o "$f.tmp" && mv "$f.tmp" "$f"; }
done
ok "piper + voz en_US-lessac-medium"

step "4/5 Hooks de los agentes"
# add_hook NOMBRE FICHERO EVENTO ENTRADA_JSON: quita la entrada anterior de english-coach y añade
# la nueva. Escribe en un temporal y solo reemplaza si jq termina bien: nunca deja el fichero vacío.
add_hook() {
  local name=$1 file=$2 event=$3 entry=$4 tmp
  mkdir -p "$(dirname "$file")"
  [[ -s $file ]] || echo '{}' >"$file"
  tmp=$(mktemp)
  if jq --arg ev "$event" --arg cmd "$CMD" --argjson entry "$entry" '
       .hooks[$ev] = ([.hooks[$ev][]? | select([.hooks[]?.command] | index($cmd) | not)] + [$entry])
     ' "$file" >"$tmp" 2>/dev/null; then
    cp "$file" "$file.bak" && mv "$tmp" "$file"
    ok "$name (${file/#$HOME/\~}, copia en .bak)"; found=1
  else
    rm -f "$tmp"
    warn "$name: no puedo leer ${file/#$HOME/\~} como JSON (¿tiene comentarios?). No lo toco; añade el hook a mano: $CMD"
  fi
}
found=0
command -v claude >/dev/null && add_hook "Claude Code" "$HOME/.claude/settings.json" UserPromptSubmit \
  "$(jq -n --arg c "$CMD" '{hooks: [{type: "command", command: $c, timeout: 5}]}')"
command -v codex >/dev/null && add_hook "Codex CLI" "$HOME/.codex/hooks.json" UserPromptSubmit \
  "$(jq -n --arg c "$CMD" '{hooks: [{type: "command", command: $c}]}')"
command -v gemini >/dev/null && add_hook "Gemini CLI" "$HOME/.gemini/settings.json" BeforeAgent \
  "$(jq -n --arg c "$CMD" '{matcher: ".*", hooks: [{type: "command", command: $c, name: "english-coach", timeout: 5000}]}')"
((found)) || warn "no encuentro claude, codex ni gemini: el tutor no se activará (los atajos sí)"

step "5/5 Atajos de Hyprland (Ctrl+Super+N traducir, Ctrl+Super+M pronunciar)"
lua=$HOME/.config/hypr/hyprland.lua conf=$HOME/.config/hypr/hyprland.conf
if [[ -f $lua ]]; then cfg=$lua; else cfg=$conf; fi
if ! command -v hyprctl >/dev/null || [[ ! -f $cfg ]]; then
  warn "no encuentro Hyprland: añade tú los atajos a lookup.sh y say.sh"
elif grep -q '>>> english-coach' "$cfg"; then
  ok "ya estaban en $cfg"
elif hyprctl binds -j | jq -e 'any(.[]; .modmask == 68 and (.key | ascii_upcase | . == "N" or . == "M"))' >/dev/null; then
  warn "Ctrl+Super+N o M ya están ocupados: no toco nada. Elige otros y apunta a $DIR/lookup.sh y $DIR/say.sh"
else
  cp "$cfg" "$cfg.bak"
  if [[ $cfg == "$lua" ]]; then
    printf '\n-- >>> english-coach >>>\nhl.bind("SUPER + CTRL + N", hl.dsp.exec_cmd("%s/lookup.sh"))\nhl.bind("SUPER + CTRL + M", hl.dsp.exec_cmd("%s/say.sh"))\n-- <<< english-coach <<<\n' "$DIR" "$DIR" >>"$cfg"
  else
    printf '\n# >>> english-coach >>>\nbind = SUPER CTRL, N, exec, %s/lookup.sh\nbind = SUPER CTRL, M, exec, %s/say.sh\n# <<< english-coach <<<\n' "$DIR" "$DIR" >>"$cfg"
  fi
  hyprctl reload >/dev/null
  ok "añadidos a $cfg (copia en $cfg.bak)"
fi

python3 "$DIR/coach.py" --test >/dev/null && python3 "$DIR/lookup.py" --test >/dev/null && ok "autotests"

cat <<EOF

Listo. Escribe en inglés a tu agente y verás las correcciones.
Selecciona una palabra y pulsa Ctrl+Super+N (traducir) o Ctrl+Super+M (escuchar).
Cuando quieras estudiar:  cd $DIR/study && claude   (o codex / gemini)
EOF
