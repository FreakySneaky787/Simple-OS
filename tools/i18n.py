#!/usr/bin/env python3
"""Simple OS – translations of Simple OS's own tools (#43). Pure Python: neither the build container nor the
developer's computer needs the gettext tools (xgettext, msgmerge, msgfmt).

  tools/i18n.py extract        collect the texts -> po/simpleos.pot; merge into every po/<lang>.po: new texts come in
                               untranslated, texts that are gone stay at the end as "#~" (obsolete), nothing is lost
  tools/i18n.py check          every po/<lang>.po: each text translated (not fuzzy), the same placeholders ({name},
                               %s, %d) in both, the PO file readable; exit 1 with a list otherwise
  tools/i18n.py build DIR      compile po/<lang>.po -> DIR/usr/share/locale/<lang>/LC_MESSAGES/simpleos.mo
                               (tools/lb_config.sh into the image; the edition package takes it from there)
  tools/i18n.py stats          translated/total per language

Where the texts come from (config/includes.chroot):
  Python tools (python shebang): _("…") with a constant string – found with the syntax tree, so an f-string can
      never sneak in: a text with a value is written _("Connected to {name}").format(name=…); N_("…") marks a text
      that is kept English in the code (keys, comparisons) and translated where it is shown, _(variable)
  shell tools (sh/bash shebang): _t "…" or _t '…' (common.sh): a constant text; values with printf:
      printf "$(_t 'Connected to %s')" "$name"
  more sources: config/i18n/extra.txt (one text per line: desktop files, menus, …, see the file)
One gettext domain "simpleos"; the Python tools load it with gettext.translation("simpleos", fallback=True), so an
English system (or a missing .mo) simply shows the English text.
"""
import ast
import os
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INC = ROOT / "config/includes.chroot"
PO_DIR = ROOT / "po"
POT = PO_DIR / "simpleos.pot"
EXTRA = ROOT / "config/i18n/extra.txt"
SCAN = ["usr/local/bin", "usr/local/sbin", "usr/local/lib/simpleos", "usr/lib/systemd/system-sleep",
        "etc/X11/Xsession.d", "usr/share/simpleos/edition/migrations"]
# _t "text", _t 'text' and a bare word: _t Strong (#174 – those were never collected, so they stayed English)
SHELL_RE = re.compile(r"""\b_t\s+(?:"((?:[^"\\$`]|\\.)*)"|'([^']*)'|([A-Za-z][A-Za-z0-9-]*)(?=$|[\s);&|]))""")
PLACEHOLDER_RE = re.compile(r"\{[a-z_][a-z0-9_]*(?:![rsa])?(?::[^{}]*)?\}|%[sd]")


# ------------------------------------------------------------------ extraction
def kind_of(path):
    try:
        first = path.open("rb").readline().decode(errors="replace")
    except OSError:
        return None
    if not first.startswith("#!"):
        # a library that the tools source (common.sh) has no "#!" line (#174)
        return "sh" if path.suffix == ".sh" else None
    if "python" in first:
        return "py"
    if re.search(r"\b(sh|bash|dash)\b", first):
        return "sh"
    return None


def python_texts(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
    except (SyntaxError, UnicodeDecodeError) as err:
        sys.exit(f"i18n: {path}: {err}")
    out = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("_", "N_")
                and node.args):
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                out.append((node.lineno, arg.value))
            elif isinstance(arg, ast.JoinedStr):
                sys.exit(f"i18n: {path}:{node.lineno}: _() with an f-string can't be translated – "
                         "use _(\"… {name} …\").format(name=…)")
            # _(variable): a text marked with N_("…") elsewhere, translated where it is shown
    return sorted(out)


def shell_unescape(text):
    return re.sub(r"\\([\\\"$`])", r"\1", text)


def shell_texts(path):
    out = []
    for no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if line.lstrip().startswith("#") or line.lstrip().startswith("_t()"):
            continue
        for m in SHELL_RE.finditer(line):
            text = shell_unescape(m.group(1)) if m.group(1) is not None else m.group(2) or m.group(3)
            if text:
                out.append((no, text))
    return out


def collect():
    """{msgid: [references]} in a stable order"""
    found = {}
    for sub in SCAN:
        base = INC / sub
        if not base.exists():
            continue
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            kind = kind_of(path)
            if not kind:
                continue
            texts = python_texts(path) if kind == "py" else shell_texts(path)
            rel = path.relative_to(INC)
            for line, text in texts:
                found.setdefault(text, []).append(f"{rel}:{line}")
    if EXTRA.exists():
        for no, line in enumerate(EXTRA.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip() and not line.startswith("#"):
                found.setdefault(line.rstrip("\n"), []).append(f"config/i18n/extra.txt:{no}")
    return found


# ------------------------------------------------------------------ PO files
def po_escape(text):
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\t", "\\t").replace("\n", "\\n")


def po_unescape(text):
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(m.group(1), m.group(1)), text)


def po_string(key, text):
    if "\n" in text[:-1]:   # several lines: like msgmerge, one PO line per text line
        parts = [p + "\n" for p in text.split("\n")]
        if text.endswith("\n"):
            parts = parts[:-1]
        else:
            parts[-1] = parts[-1][:-1]
        return f'{key} ""\n' + "".join(f'"{po_escape(p)}"\n' for p in parts if p)
    return f'{key} "{po_escape(text)}"\n'


def read_po(path):
    """[{id, str, refs, flags, obsolete, comments}] incl. the header (id "")"""
    entries, cur, field = [], None, None

    def flush():
        nonlocal cur
        if cur is not None and cur.get("id") is not None:
            entries.append(cur)
        cur = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        obsolete = raw.startswith("#~")
        line = raw[2:].strip() if obsolete else raw.strip()
        if not line:
            flush()
            continue
        if cur is None:
            cur = {"id": None, "str": "", "refs": [], "flags": set(), "obsolete": obsolete, "comments": []}
        if raw.startswith("#:"):
            cur["refs"] += raw[2:].split()
        elif raw.startswith("#,"):
            cur["flags"] |= {f.strip() for f in raw[2:].split(",")}
        elif raw.startswith("# ") or raw == "#":
            cur["comments"].append(raw)
        elif line.startswith("msgid "):
            if cur.get("id") is not None:   # two entries without a blank line between them
                flush()
                cur = {"id": None, "str": "", "refs": [], "flags": set(), "obsolete": obsolete, "comments": []}
            cur["id"], field = po_unescape(line[7:-1]), "id"
        elif line.startswith("msgstr "):
            cur["str"], field = po_unescape(line[8:-1]), "str"
        elif line.startswith('"') and field:
            cur[field] += po_unescape(line[1:-1])
        elif line.startswith("#"):
            continue
        else:
            raise ValueError(f"{path}: cannot read line: {raw}")
    flush()
    return entries


def header(lang=None):
    return ("Project-Id-Version: Simple OS\n"
            "Report-Msgid-Bugs-To: https://github.com/FreakySneaky787/Simple-OS/issues\n"
            + (f"Language: {lang}\n" if lang else "")
            + "MIME-Version: 1.0\nContent-Type: text/plain; charset=UTF-8\nContent-Transfer-Encoding: 8bit\n")


def write_po(path, entries, lang):
    out = ["# Simple OS – translations of Simple OS's own tools (#43). Edit the msgstr lines; after changing the tools\n"
           "# run ./tools/i18n.py extract (new texts appear here empty) and ./tools/i18n.py check.\n"]
    out.append('msgid ""\n' + po_string("msgstr", header(lang)) + "\n")
    for e in entries:
        if e["id"] == "":
            continue
        block = "".join(c + "\n" for c in e.get("comments", []))
        if e.get("refs") and not e.get("obsolete"):
            block += "#: " + " ".join(e["refs"]) + "\n"
        flags = sorted(e.get("flags", set()) - {""})
        if flags:
            block += "#, " + ", ".join(flags) + "\n"
        body = po_string("msgid", e["id"]) + po_string("msgstr", e["str"])
        if e.get("obsolete"):
            body = "".join("#~ " + ln + "\n" for ln in body.splitlines())
        out.append(block + body + "\n")
    path.write_text("".join(out), encoding="utf-8")


def extract():
    found = collect()
    PO_DIR.mkdir(exist_ok=True)
    write_po(POT, [{"id": k, "str": "", "refs": v} for k, v in found.items()], None)
    for po in sorted(PO_DIR.glob("*.po")):
        old = {e["id"]: e for e in read_po(po) if e["id"]}
        entries = []
        for msgid, refs in found.items():
            e = old.pop(msgid, None) or {"id": msgid, "str": "", "flags": set(), "comments": []}
            e.update(refs=refs, obsolete=False)
            entries.append(e)
        for e in old.values():
            if e.get("str"):
                e["obsolete"] = True
                entries.append(e)
        write_po(po, entries, po.stem)
    print(f"i18n: {len(found)} texts -> {POT.relative_to(ROOT)}")


def placeholders(text):
    return sorted(PLACEHOLDER_RE.findall(text))


def check():
    problems = []
    found = set(collect())
    pos = sorted(PO_DIR.glob("*.po"))
    if not pos:
        problems.append("no po/<lang>.po")
    for po in pos:
        try:
            entries = [e for e in read_po(po) if e["id"] and not e["obsolete"]]
        except ValueError as err:
            problems.append(str(err))
            continue
        ids = {e["id"] for e in entries}
        for missing in sorted(found - ids):
            problems.append(f"{po.name}: not in the file (run tools/i18n.py extract): {missing[:70]!r}")
        for e in entries:
            if e["id"] not in found:
                problems.append(f"{po.name}: no longer used (run tools/i18n.py extract): {e['id'][:70]!r}")
            elif not e["str"] or "fuzzy" in e["flags"]:
                problems.append(f"{po.name}: not translated: {e['id'][:70]!r}")
            elif placeholders(e["id"]) != placeholders(e["str"]):
                problems.append(f"{po.name}: placeholders differ: {e['id'][:60]!r} -> {e['str'][:60]!r}")
            elif e["id"].endswith("\n") != e["str"].endswith("\n"):
                problems.append(f"{po.name}: line end differs: {e['id'][:60]!r}")
            elif e["id"].startswith(" ") != e["str"].startswith(" ") or e["id"].endswith(" ") != e["str"].endswith(" "):
                # texts that are glued to others (" · needs password", "Main · ") lose their gap otherwise
                problems.append(f"{po.name}: space at the start or end differs: {e['id'][:60]!r} -> {e['str'][:60]!r}")
    for p in problems:
        print(p)
    print(f"i18n check: {'OK' if not problems else str(len(problems)) + ' problem(s)'}")
    return 0 if not problems else 1


def write_mo(path, catalog):
    """GNU .mo (little endian, no hash table)"""
    keys = sorted(catalog)
    ids = b"".join(k.encode() + b"\0" for k in keys)
    strs = b"".join(catalog[k].encode() + b"\0" for k in keys)
    n = len(keys)
    start = 7 * 4 + n * 16
    ofs_ids, ofs_strs, pos = [], [], 0
    for k in keys:
        ofs_ids.append((len(k.encode()), start + pos))
        pos += len(k.encode()) + 1
    base, pos = start + len(ids), 0
    for k in keys:
        ofs_strs.append((len(catalog[k].encode()), base + pos))
        pos += len(catalog[k].encode()) + 1
    out = struct.pack("<7I", 0x950412de, 0, n, 7 * 4, 7 * 4 + n * 8, 0, 0)
    out += b"".join(struct.pack("<2I", ln, of) for ln, of in ofs_ids)
    out += b"".join(struct.pack("<2I", ln, of) for ln, of in ofs_strs)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(out + ids + strs)
    os.replace(tmp, path)


def build(dest):
    for po in sorted(PO_DIR.glob("*.po")):
        catalog = {"": header(po.stem)}
        for e in read_po(po):
            if e["id"] and e["str"] and not e["obsolete"] and "fuzzy" not in e["flags"]:
                catalog[e["id"]] = e["str"]
        mo = Path(dest) / "usr/share/locale" / po.stem / "LC_MESSAGES/simpleos.mo"
        write_mo(mo, catalog)
        print(f"i18n: {po.name} -> {mo} ({len(catalog) - 1} texts)")


def stats():
    total = len(collect())
    for po in sorted(PO_DIR.glob("*.po")):
        done = sum(1 for e in read_po(po) if e["id"] and e["str"] and not e["obsolete"] and "fuzzy" not in e["flags"])
        print(f"{po.stem}: {done}/{total}")


def main(argv):
    if len(argv) >= 2 and argv[1] == "extract":
        extract()
        return 0
    if len(argv) >= 2 and argv[1] == "check":
        return check()
    if len(argv) >= 3 and argv[1] == "build":
        build(argv[2])
        return 0
    if len(argv) >= 2 and argv[1] == "stats":
        stats()
        return 0
    print(__doc__.strip().split("\n\n")[1])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
