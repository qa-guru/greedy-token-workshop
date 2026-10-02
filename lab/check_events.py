#!/usr/bin/env python3
"""Check events fixture has id+ts+event.

Smoke: python3 lab/check_events.py lab/events.jsonl
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main(path: Path) -> dict:
    if not path.is_file():
        return {"ok": False, "error": f"missing: {path}"}
    missing = []
    count = 0
    try:
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            count += 1
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                missing.append({"line": i, "missing": ["id", "ts", "event"]})
                continue
            holes = [k for k in ("id", "ts", "event") if k not in e or e[k] in (None, "")]
            if holes:
                missing.append({"line": i, "missing": holes})
    except OSError as exc:
        return {"ok": False, "error": f"read failed: {exc}"}
    return {"ok": not missing, "count": count, "missing": missing}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"ok": False, "error": "usage: check_events.py FILE"}, ensure_ascii=False))
        sys.exit(2)
    result = main(Path(sys.argv[1]))
    print(json.dumps(result, ensure_ascii=False))
    if "error" in result:
        sys.exit(2)
    sys.exit(0 if result["ok"] else 1)
