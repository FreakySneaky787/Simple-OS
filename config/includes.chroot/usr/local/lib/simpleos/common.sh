# Simple OS – shared helpers of the Rofi tools (simpleos-wifi, -powermenu, -update, -help, -usb-notify).
# Include with ". /usr/local/lib/simpleos/common.sh" after SOS_NAME=<tool> (log name, notification sender).
# Pure POSIX sh (dash), no set -e/-u: every caller ends with exit 0 itself and a clear
# notification. Technical details go to ~/.cache/<SOS_NAME>.log.

SOS_NAME=${SOS_NAME:-simpleos}
SOS_TITLE=${SOS_TITLE:-Simple OS}
SOS_ICON=${SOS_ICON:-dialog-information}
SOS_NL='
'

# Error output into the log instead of nowhere (taskbar, Openbox and udiskie discard stderr)
sos_log_init() {
    SOS_LOG_DIR=${XDG_CACHE_HOME:-${HOME:-/tmp}/.cache}
    mkdir -p "$SOS_LOG_DIR" 2>/dev/null || SOS_LOG_DIR=/tmp
    SOS_LOG=$SOS_LOG_DIR/$SOS_NAME.log
    [ -f "$SOS_LOG" ] && [ "$(wc -c < "$SOS_LOG" 2>/dev/null || echo 0)" -gt 100000 ] && rm -f "$SOS_LOG"
    # exec with a failing redirection would end dash -> only redirect if the file is writable
    touch "$SOS_LOG" 2>/dev/null && [ -w "$SOS_LOG" ] && exec 2>>"$SOS_LOG"
    echo "--- $(date '+%F %T' 2>/dev/null) $SOS_NAME $*" >&2
}
sos_log() { echo "$SOS_NAME: $*" >&2; }

# sos_notify "text" [low|normal|critical]
# Category x-simpleos: the dunst battery filter (simpleos-dunst) lets our own notifications like "Power" through
sos_notify() {
    sos_log "notify: $1"
    command -v notify-send >/dev/null && notify-send -u "${2:-normal}" -c x-simpleos -a "$SOS_TITLE" -i "$SOS_ICON" "$SOS_TITLE" "$1" || true
}
# sos_ask "title" "text" "button" -> exit 0 if the button (or the notification itself) was clicked.
# notify-send -A waits for the click; without notify-send or without a click -> 1.
sos_ask() {
    command -v notify-send >/dev/null || return 1
    sos_log "ask: $1 – $2"
    answer=$(notify-send -c x-simpleos -a "$SOS_TITLE" -i "$SOS_ICON" -A "yes=$3" -A "default=$3" "$1" "$2" 2>/dev/null)
    case "$answer" in yes|default) return 0 ;; esac
    return 1
}

sos_esc() { printf '%s' "$1" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g'; }
sos_is_num() { case "$1" in ''|*[!0-9]*) return 1 ;; esac; return 0; }
# FontAwesome 4 (like the taskbar), $1 = UTF-8 as an octal escape
sos_fa() { printf "<span font_desc='FontAwesome 11'>%s</span>" "$(printf "$1")"; }
# Quiet addition in a menu row ("Connected", "Good" …)
sos_dim() { printf "<span alpha='55%%'>%s</span>" "$(sos_esc "$1")"; }

# Rofi does not start at all -> sos_rofi_failed (callers can override the function)
sos_rofi_failed() {
    sos_notify "This window could not open. Please try again." critical
    exit 0
}
# Rofi with retries: Esc -> empty output, any other error -> sos_rofi_failed. A new attempt (every 0.3 s,
# up to 6 times) on
#   - grab errors: right after a taskbar click the mouse click still holds keyboard/mouse
#   - "Rofi already running" (lock file): flyouts started by a click in the start menu (Wi-Fi, Sound, Appearance …)
#     arrive while the start menu Rofi is still closing – Rofi allows only one instance
sos_rofi() {
    command -v rofi >/dev/null || { sos_log "rofi missing"; sos_rofi_failed; }
    rin=$(mktemp) || { sos_log "mktemp failed"; sos_rofi_failed; }
    rerr=$(mktemp) || { rm -f "$rin"; sos_rofi_failed; }
    cat > "$rin"
    rc=1 out= try=0
    while [ "$try" -lt 6 ]; do
        try=$((try + 1))
        out=$(rofi "$@" < "$rin" 2>"$rerr"); rc=$?
        [ "$rc" -eq 0 ] && break
        [ -s "$rerr" ] || break                          # Esc: code 1 without a message
        cat "$rerr" >&2
        grep -qiE 'grab|already running|pidfile' "$rerr" || break   # only these are worth another attempt
        sleep 0.3
    done
    failed=0
    [ "$rc" -ne 0 ] && grep -qiE 'grab|display|fail|error|cannot|unable' "$rerr" && failed=1
    rm -f "$rin" "$rerr"
    [ "$failed" = 1 ] && sos_rofi_failed
    [ "$rc" -eq 0 ] && printf '%s' "$out"
    return 0
}

# Flyout position like Windows 11: SOS_CORNER=1 -> on the right above the taskbar (or below it if the
# bar is at the top via the designer); otherwise centered. 60 px = 40 px bar + 10 px gap + 10 px air.
sos_position() {
    [ "${SOS_CORNER:-0}" = 1 ] || { echo "location: center; anchor: center;"; return 0; }
    pos=$(sed -n 's/^position=//p' "${HOME:-/tmp}/.config/simpleos/taskbar" 2>/dev/null)
    if [ "$pos" = top ]; then echo "location: north east; anchor: north east; x-offset: -12px; y-offset: 60px;"
    else echo "location: south east; anchor: south east; x-offset: -12px; y-offset: -60px;"; fi
}

# Menu from rows with a hidden action: sos_add "display (markup)" "action<TAB>data…";
# sos_pick "heading" [width] sets $action/$arg1/$arg2 (empty on Esc)
SOS_ROWS= SOS_ACTS=
sos_add() { SOS_ROWS="$SOS_ROWS$1$SOS_NL"; SOS_ACTS="$SOS_ACTS$2$SOS_NL"; }
sos_pick() {
    lines=$(printf '%s' "$SOS_ROWS" | grep -c . || true)
    # Flyout like Windows 11: a heading instead of a search field (typing still filters), Inter instead of monospace
    idx=$(printf '%s' "$SOS_ROWS" | sos_rofi -dmenu -i -no-custom -format i -markup-rows -p "${SOS_PROMPT:-$SOS_TITLE}" \
        -mesg "$1" -theme-str "window { width: ${2:-440}px; $(sos_position) } mainbox { children: [ message, listview ]; }
                              listview { lines: ${lines:-8}; } element-icon { enabled: false; }
                              textbox { text-color: @fg; }")
    action= arg1= arg2=
    if sos_is_num "$idx"; then
        line=$(printf '%s' "$SOS_ACTS" | sed -n "$((idx + 1))p")
        action=$(printf '%s' "$line" | cut -f1)
        arg1=$(printf '%s' "$line" | cut -f2)
        arg2=$(printf '%s' "$line" | cut -f3)
    fi
    SOS_ROWS= SOS_ACTS=
}
