# Simple OS – translations of the shell tools (#43). Sourced by common.sh and by the tools that do not use it
# (root helpers, screenshot …): ". /usr/local/lib/simpleos/i18n.sh". POSIX sh, safe with "set -u".
# _t "English text" prints the text in the system language (gettext, domain "simpleos",
# /usr/share/locale/<lang>/LC_MESSAGES/simpleos.mo); a text with values goes through printf:
#   printf "$(_t 'Connected to %s')" "$name"
# Always the language of the session or – root via pkexec has no LANG – of the system (/etc/default/locale): many
# tools set LC_ALL=C to read command output, which would otherwise turn every message English. tools/i18n.py finds
# the texts by "_t".
TEXTDOMAIN=simpleos
export TEXTDOMAIN
SOS_LANG=${LANG:-}
case "$SOS_LANG" in
    ""|C|C.*|POSIX) SOS_LANG=$(sed -n 's/^LANG="\{0,1\}\([^"]*\)"\{0,1\}$/\1/p' "${SIMPLEOS_LOCALE_FILE:-/etc/default/locale}" 2>/dev/null | head -n 1) ;;
esac
# Root helpers (no LANG): our Python filters (progress-filter) find the language through LANGUAGE; C programs ignore it
# without a LANG, so apt's and dpkg's output – which the helpers read – stays English
if [ -z "${LANG:-}" ] && [ -z "${LANGUAGE:-}" ] && [ -n "$SOS_LANG" ]; then
    LANGUAGE=${SOS_LANG%%.*}
    export LANGUAGE
fi
if command -v gettext >/dev/null 2>&1 && [ -n "$SOS_LANG" ]; then
    _t() { LC_ALL=$SOS_LANG gettext -- "$1" 2>/dev/null || printf '%s' "$1"; }
else
    _t() { printf '%s' "$1"; }
fi
