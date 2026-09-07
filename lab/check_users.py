#!/usr/bin/env python3
"""Check users fixture has id+email.

Smoke: python3 lab/check_users.py lab/users.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main(path: Path) -> dict:
    if not path.is_file():
        return {"ok": False, "error": f"missing: {path}"}
    try:
        users = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"ok": False, "error": f"invalid json: {exc}"}
    if not isinstance(users, list):
        return {"ok": False, "error": "expected a JSON array"}
    missing = []
    for i, u in enumerate(users):
        if not isinstance(u, dict):
            missing.append({"index": i, "missing": ["id", "email"]})
            continue
        holes = [k for k in ("id", "email") if k not in u or u[k] in (None, "")]
        if holes:
            missing.append({"index": i, "missing": holes})
    return {"ok": not missing, "count": len(users), "missing": missing}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"ok": False, "error": "usage: check_users.py FILE"}, ensure_ascii=False))
        sys.exit(2)
    result = main(Path(sys.argv[1]))
    print(json.dumps(result, ensure_ascii=False))
    if "error" in result:
        sys.exit(2)
    sys.exit(0 if result["ok"] else 1)
