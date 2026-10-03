# Simple OS – gemeinsame Helfer der Rofi-Werkzeuge (simpleos-wifi, -powermenu, -update, -help, -usb-notify).
# Einbinden mit ". /usr/local/lib/simpleos/common.sh" nach SOS_NAME=<werkzeug> (Log-Name, Meldungs-Absender).
# Reines POSIX-sh (dash), kein set -e/-u: jeder Aufrufer endet selbst mit Exit 0 und einer verständlichen
# Meldung. Technische Details landen in ~/.cache/<SOS_NAME>.log.

SOS_NAME=${SOS_NAME:-simpleos}
SOS_TITLE=${SOS_TITLE:-Simple OS}
SOS_ICON=${SOS_ICON:-dialog-information}
SOS_NL='
'

# Fehlerausgaben ins Log statt ins Leere (Taskleiste, Openbox und udiskie verwerfen stderr)
sos_log_init() {
    SOS_LOG_DIR=${XDG_CACHE_HOME:-${HOME:-/tmp}/.cache}
    mkdir -p "$SOS_LOG_DIR" 2>/dev/null || SOS_LOG_DIR=/tmp
    SOS_LOG=$SOS_LOG_DIR/$SOS_NAME.log
    [ -f "$SOS_LOG" ] && [ "$(wc -c < "$SOS_LOG" 2>/dev/null || echo 0)" -gt 100000 ] && rm -f "$SOS_LOG"
    # exec mit fehlschlagender Umleitung würde dash beenden -> nur umleiten, wenn die Datei beschreibbar ist
    touch "$SOS_LOG" 2>/dev/null && [ -w "$SOS_LOG" ] && exec 2>>"$SOS_LOG"
    echo "--- $(date '+%F %T' 2>/dev/null) $SOS_NAME $*" >&2
}
sos_log() { echo "$SOS_NAME: $*" >&2; }

# sos_notify "Text" [low|normal|critical]
# Kategorie x-simpleos: der dunst-Akku-Filter (simpleos-dunst) lässt eigene Meldungen wie "Power" durch
sos_notify() {
    sos_log "notify: $1"
    command -v notify-send >/dev/null && notify-send -u "${2:-normal}" -c x-simpleos -a "$SOS_TITLE" -i "$SOS_ICON" "$SOS_TITLE" "$1" || true
}
# sos_ask "Titel" "Text" "Knopf" -> Exit 0, wenn der Knopf (oder die Meldung selbst) angeklickt wurde.
# notify-send -A wartet auf den Klick; ohne notify-send oder ohne Klick -> 1.
sos_ask() {
    command -v notify-send >/dev/null || return 1
    sos_log "ask: $1 – $2"
    answer=$(notify-send -c x-simpleos -a "$SOS_TITLE" -i "$SOS_ICON" -A "yes=$3" -A "default=$3" "$1" "$2" 2>/dev/null)
    case "$answer" in yes|default) return 0 ;; esac
    return 1
}

sos_esc() { printf '%s' "$1" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g'; }
sos_is_num() { case "$1" in ''|*[!0-9]*) return 1 ;; esac; return 0; }
# FontAwesome 4 (wie die Taskleiste), $1 = UTF-8 als Oktal-Escape
sos_fa() { printf "<span font_desc='FontAwesome 11'>%s</span>" "$(printf "$1")"; }
# Leiser Zusatz in einer Menüzeile ("Connected", "Good" …)
sos_dim() { printf "<span alpha='55%%'>%s</span>" "$(sos_esc "$1")"; }

# Rofi startet gar nicht -> sos_rofi_failed (Aufrufer kann die Funktion überschreiben)
sos_rofi_failed() {
    sos_notify "This window could not open. Please try again." critical
    exit 0
}
# Rofi mit Wiederholung: Esc -> leere Ausgabe, sonstiger Fehler -> sos_rofi_failed. Neuer Versuch (alle 0,3 s,
# bis zu 6-mal) bei
#   - Grab-Fehlern: direkt nach einem Taskleisten-Klick hält der Mausklick Tastatur/Maus noch fest
#   - "Rofi already running" (Sperrdatei): per Klick im Startmenü gestartete Flyouts (WLAN, Sound, Appearance …)
#     kommen, während das Startmenü-Rofi sich noch beendet – Rofi lässt nur eine Instanz zu
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
        [ -s "$rerr" ] || break                          # Esc: Code 1 ohne Meldung
        cat "$rerr" >&2
        grep -qiE 'grab|already running|pidfile' "$rerr" || break   # nur diese lohnen einen neuen Versuch
        sleep 0.3
    done
    failed=0
    [ "$rc" -ne 0 ] && grep -qiE 'grab|display|fail|error|cannot|unable' "$rerr" && failed=1
    rm -f "$rin" "$rerr"
    [ "$failed" = 1 ] && sos_rofi_failed
    [ "$rc" -eq 0 ] && printf '%s' "$out"
    return 0
}

# Flyout-Position wie bei Windows 11: SOS_CORNER=1 -> rechts über der Taskleiste (bzw. darunter, wenn die
# Leiste per Designer oben liegt); sonst mittig. 60 px = 40 px Leiste + 10 px Abstand + 10 px Luft.
sos_position() {
    [ "${SOS_CORNER:-0}" = 1 ] || { echo "location: center; anchor: center;"; return 0; }
    pos=$(sed -n 's/^position=//p' "${HOME:-/tmp}/.config/simpleos/taskbar" 2>/dev/null)
    if [ "$pos" = top ]; then echo "location: north east; anchor: north east; x-offset: -12px; y-offset: 60px;"
    else echo "location: south east; anchor: south east; x-offset: -12px; y-offset: -60px;"; fi
}

# Menü aus Zeilen mit versteckter Aktion: sos_add "Anzeige (Markup)" "Aktion<TAB>Daten…";
# sos_pick "Kopfzeile" [Breite] setzt $action/$arg1/$arg2 (leer bei Esc)
SOS_ROWS= SOS_ACTS=
sos_add() { SOS_ROWS="$SOS_ROWS$1$SOS_NL"; SOS_ACTS="$SOS_ACTS$2$SOS_NL"; }
sos_pick() {
    lines=$(printf '%s' "$SOS_ROWS" | grep -c . || true)
    # Flyout wie bei Windows 11: Überschrift statt Suchfeld (Tippen filtert trotzdem), Inter statt Monospace
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
