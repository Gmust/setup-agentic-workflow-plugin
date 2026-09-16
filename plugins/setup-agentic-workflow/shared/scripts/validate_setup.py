"""Read-only checks for agent entry points and explicitly linked local files."""

import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


def validate(root, agents, documents=(), claude_file="CLAUDE.md"):
    root = Path(root).resolve()
    errors, warnings, checked = [], [], set()
    visited = set()
    counts = {"local_links": 0, "imports": 0}

    def origin(source):
        return " (in " + source + ")" if source else ""

    def resolve(path, file_required=True, source=None, reference=None):
        shown = reference or path.name
        try:
            target = path.resolve()
            target.relative_to(root)
        except (ValueError, OSError, RuntimeError):
            errors.append("Reference escapes repository or cannot be resolved: "
                          + shown + origin(source))
            return None
        if not target.exists() or (file_required and not target.is_file()):
            errors.append("Missing file: " + target.relative_to(root).as_posix()
                          + origin(source))
            return None
        return target

    def inspect(path, imports=False, chain=(), source=None, reference=None):
        target = resolve(path, True, source, reference)
        if target is None:
            return
        label = target.relative_to(root).as_posix()
        if target in chain:
            errors.append("Import cycle at: " + label)
            return
        if len(chain) > 4:
            errors.append("Import depth exceeds four hops at: " + label)
            return
        key = (target, imports, chain if imports else ())
        if key in visited:
            return
        visited.add(key)
        checked.add(label)
        if target.stat().st_size > 262144:
            warnings.append("File exceeds inspection size limit: " + label)
            return
        try:
            content = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            errors.append("Cannot read UTF-8 document: " + label)
            return
        if not content.strip():
            errors.append("Empty document: " + label)
        # Simple Markdown subset; use a Markdown parser if rich syntax is needed.
        fence = None
        indented_code = False
        previous_blank = True
        for raw in content.splitlines():
            marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", raw)
            if marker:
                value = marker[1]
                if fence is None:
                    fence = value
                elif value[0] == fence[0] and len(value) >= len(fence):
                    fence = None
                indented_code = False
                previous_blank = False
                continue
            if fence:
                continue
            stripped = raw.strip()
            if not stripped:
                previous_blank = True
                continue
            if (re.match(r"^(?: {4,}|\t)", raw)
                    and (indented_code or previous_blank)
                    and not re.match(r"^(?:[-*+]|\d+[.)])\s", stripped)):
                indented_code = True
                previous_blank = False
                continue
            indented_code = False
            previous_blank = False
            line = re.sub(r"(`+).*?\1", "", raw)
            links = re.findall(r"\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\)", line)
            for link in links:
                link = link.strip("<>")
                if "(" in link or ")" in link:
                    warnings.append("Complex Markdown link needs manual review: " + label)
                    continue
                try:
                    parsed = urlsplit(link)
                except ValueError:
                    warnings.append("Unparsed link needs manual review: " + label)
                    continue
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                counts["local_links"] += 1
                resolve(target.parent / unquote(parsed.path), file_required=False,
                        source=label, reference=link)
            if re.search(r"\[[^\]]+\]\[|^\s*\[[^\]]+\]:", line):
                warnings.append("Reference-style link needs manual review: " + label)
            if imports and "@" in line:
                match = re.fullmatch(r"\s*@([^\s]+)\s*", line)
                if not match:
                    warnings.append("Inline @ reference needs manual review: " + label)
                    continue
                value = match[1]
                if value.startswith("~") or ":" in value or "\\" in value:
                    errors.append("Non-relative import needs manual review: "
                                  + label + " -> " + value)
                    continue
                counts["imports"] += 1
                inspect(target.parent / value, True, chain + (target,), label, value)

    if "codex" in agents:
        inspect(root / "AGENTS.md")
    if "claude" in agents:
        inspect(root / claude_file, True)
    for document in documents:
        inspect(root / document)
    return {
        "ok": not errors,
        "checked": sorted(checked),
        "verified": {
            "documents": len(checked),
            "local_links": counts["local_links"],
            "imports": counts["imports"],
        },
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "limits": '"ok" only means nothing checked failed; read "verified" for how much was actually checked. Simple inline links and standalone imports only; fenced and indented code blocks are skipped; anchors, command behavior, and agent activation require manual verification.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--agents", nargs="+", choices=("codex", "claude"), required=True)
    parser.add_argument("--claude-file", default="CLAUDE.md")
    parser.add_argument("--document", action="append", default=[])
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error("root must be an existing directory")
    result = validate(args.root, args.agents, args.document, args.claude_file)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
