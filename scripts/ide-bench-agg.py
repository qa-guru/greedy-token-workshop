#!/usr/bin/env python3
"""Aggregate both runs: per-cell naive/greedy totals, saved tokens and $."""
import json, sqlite3

DB = "/Users/stanislav/.local/share/devin/cli/sessions.db"
src = open('/Users/stanislav/greedy-token-workshop/scripts/ide-bench.py').read().split('def run_one')[0]
exec(src)

RATES = {
    "gpt-6-1-sol-max": (2.0, 0.1, 10.0),
    "kimi-k3-max": (3.0, 0.3, 15.0),
    "claude-opus-5-5-max": (4.0, 0.2, 20.0),
}

def cost(model, m):
    i, c, o = RATES[model]
    return (m["input"] * i + m.get("cache_create", 0) * i
            + m["cache_read"] * c + m["output"] * o) / 1e6

con = sqlite3.connect(DB)
legs = {}
for fname, run in (("/tmp/gt-ide-bench-run1.jsonl", 1), ("/tmp/gt-ide-bench.jsonl", 2)):
    for line in open(fname):
        rec = json.loads(line)
        if not rec.get("sid"):
            continue
        m = session_metrics(con, rec["sid"])
        legs[(rec["tag"], run)] = dict(metrics=m, cost=cost(rec["model_arg"], m),
                                     wall=rec["wall_s"], sid=rec["sid"])

print(f"{'pair':4} {'model':5} | {'n1':>7} {'g1':>7} {'s1':>7} | {'n2':>7} {'g2':>7} {'s2':>7} | {'$1':>7} {'$2':>7}")
tot_s = []
tot_c = []
for pair in PAIRS:
    for name, mid in MODELS.items():
        c1, c2 = [], []
        for run in (1, 2):
            n, g = legs.get((f"{pair}-naive-{name}", run)), legs.get((f"{pair}-greedy-{name}", run))
            if n and g:
                c1.append((n, g)) if run == 1 else c2.append((n, g))
        n1, g1 = legs.get((f"{pair}-naive-{name}", 1), {}), legs.get((f"{pair}-greedy-{name}", 1), {})
        n2, g2 = legs.get((f"{pair}-naive-{name}", 2), {}), legs.get((f"{pair}-greedy-{name}", 2), {})
        def t(x): return x["metrics"]["total"] if x else 0
        def s(n, g): return t(n) - t(g) if n and g else 0
        def dc(n, g): return n["cost"] - g["cost"] if n and g else 0
        s1, s2 = s(n1, g1), s(n2, g2)
        d1, d2 = dc(n1, g1), dc(n2, g2)
        tot_s += [s1, s2]; tot_c += [d1, d2]
        print(f"{pair:4} {name:5} | {t(n1):>7} {t(g1):>7} {s1:>+7} | {t(n2):>7} {t(g2):>7} {s2:>+7} | {d1:>+7.3f} {d2:>+7.3f}")

pos = sum(1 for s in tot_s if s > 50)
neg = sum(1 for s in tot_s if s < -50)
print(f"\ncells +/>50: {pos}/36   -/<-50: {neg}/36   noise: {36-pos-neg}/36")
print(f"sum saved = {sum(tot_s):,} tok   sum $ = {sum(tot_c):+.3f}")
