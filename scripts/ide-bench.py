#!/usr/bin/env python3
"""IDE-usage benchmark: run devin -p sessions, read real token metrics from sessions.db.

Design: 6 prompt pairs x 3 models x 2 arms (naive vs greedy) = 36 legs.
Naive legs run in a neutral /tmp dir (no .greedy-token.yaml, no rules).
Greedy legs run in the workshop and must use the greedy-token CLI.
Each -p invocation creates a fresh session; matched by working_directory+created_at.
"""
import json, os, sqlite3, subprocess, sys, time
from pathlib import Path

DEVIN = "/Applications/Devin.app/Contents/Resources/app/extensions/windsurf/devin/bin/devin"
DB = "/Users/stanislav/.local/share/devin/cli/sessions.db"
WORKSHOP = "/Users/stanislav/greedy-token-workshop"
GT = "/Users/stanislav/zero-design-system/projects/greedy-token-home/dev/.venv/bin/greedy-token"
OUT = Path("/tmp/gt-ide-bench.jsonl")

MODELS = {
    "sol": "gpt-6-1-sol-max",
    "kimi": "kimi-k3-max",
    "opus": "claude-opus-5-5-max",
}
NAIVE_DIR = "/tmp/gt-naive-ws"   # neutral cwd — no .greedy-token.yaml, no greedy MCP

PAIRS = {
    "A": {
        "naive": "Проверь, что в файле /Users/stanislav/greedy-token-workshop/lab/users.json у каждого объекта есть ключи id и email. Скажи, у какого объекта чего не хватает.",
        "greedy": f"Не читай файл сам. Выполни в терминале: cd {WORKSHOP} && {GT} run \"в lab/users.json у каждого объекта есть id и email\" --execute — и доложи что вывело.",
    },
    "B": {
        "naive": "Найди все строки с \"email\" в /Users/stanislav/greedy-token-workshop/lab/ и покажи их.",
        "greedy": f"Не используй Grep сам. Выполни в терминале: cd {WORKSHOP} && {GT} run \"find email in lab/users.json\" --execute — и доложи что вывело.",
    },
    "C": {
        "naive": "Как в этом проекте принято проверять ключи id и email у users? Найди ответ в документации /Users/stanislav/greedy-token-workshop/docs/.",
        "greedy": f"Не читай файлы сам. Выполни в терминале: cd {WORKSHOP} && {GT} rag \"как у нас принято проверять ключи id email у users\" — и доложи что вывело.",
    },
    "D": {
        "naive": "Прочитай /Users/stanislav/greedy-token-workshop/lab/users.json и верни JSON [{index, has_id, has_email}] для каждого объекта.",
        "greedy": f"Не читай файл сам. Выполни в терминале: cd {WORKSHOP} && {GT} llm \"classify users\" --execute — и доложи что вывело.",
    },
    "E": {
        "naive": "Отрефактори архитектуру конфигуратора: разбей на компоненты, предложи структуру и первые шаги. Код не пиши.",
        "greedy": f"Выполни в терминале: cd {WORKSHOP} && {GT} route \"отрефактори архитектура конфигуратора\" — покажи какой тир выбран; затем ответь на вопрос сам (код не пиши).",
    },
    "F": {
        "naive": "У всех юзеров в /Users/stanislav/greedy-token-workshop/lab/users.json проверь наличие ключей и скажи, где чего нет.",
        "greedy": f"Выполни в терминале: cd {WORKSHOP} && {GT} route \"у всех юзеров в users.json проверь наличие ключей\" — покажи тир; если cursor-fallback — ответь сам.",
    },
}

CHILD_ENV = {k: v for k, v in os.environ.items()
             if k != "ACP_BACKEND" and not k.startswith(("WINDSURF_", "ELECTRON_", "CHISEL_"))}


def session_metrics(con, sid):
    rows = con.execute("""
        SELECT DISTINCT json_extract(chat_message,'$.message_id'),
               json_extract(chat_message,'$.metadata.metrics')
        FROM message_nodes
        WHERE session_id=? AND json_extract(chat_message,'$.metadata.metrics.input_tokens') IS NOT NULL
    """, (sid,))
    inp = out = cr = cc = 0
    for _mid, mraw in rows:
        m = json.loads(mraw)
        inp += m.get("input_tokens") or 0
        out += m.get("output_tokens") or 0
        cr += m.get("cache_read_tokens") or 0
        cc += m.get("cache_creation_tokens") or 0
    tools = []
    seen_tc = set()
    for tc_raw, in con.execute("""
        SELECT DISTINCT chat_message FROM message_nodes
        WHERE session_id=? AND json_extract(chat_message,'$.tool_calls') IS NOT NULL
    """, (sid,)):
        try:
            for tc in json.loads(tc_raw).get("tool_calls") or []:
                if tc.get("id") not in seen_tc:
                    seen_tc.add(tc.get("id"))
                    tools.append(tc.get("name"))
        except Exception:
            pass
    return dict(input=inp, cache_read=cr, cache_create=cc, output=out,
                total=inp + cr + cc + out, n_tool_calls=len(tools), tools=tools)


def run_one(tag, model_arg, prompt, cwd):
    Path(cwd).mkdir(parents=True, exist_ok=True)
    cwd_res = str(Path(cwd).resolve())
    con = sqlite3.connect(DB)
    before = {r[0] for r in con.execute("SELECT id FROM sessions")}
    t0 = int(time.time()) - 5
    con.close()
    start = time.time()
    try:
        proc = subprocess.run(
            [DEVIN, "-p", prompt, "--model", model_arg,
             "--permission-mode", "dangerous",
             "--respect-workspace-trust", "false"],
            cwd=cwd, env=CHILD_ENV, capture_output=True, text=True, timeout=900)
        rc, tail, err = proc.returncode, proc.stdout[-800:], proc.stderr[-400:]
    except subprocess.TimeoutExpired:
        rc, tail, err = -9, "", "TIMEOUT 900s"
    wall = time.time() - start
    con = sqlite3.connect(DB)
    news = [r for r in con.execute(
        "SELECT id, working_directory, created_at FROM sessions WHERE created_at >= ?", (t0,))
        if r[0] not in before]
    cands = [r for r in news if r[1] and str(Path(r[1]).resolve()) == cwd_res]
    sid = cands[0][0] if len(cands) == 1 else (news[0][0] if len(news) == 1 else None)
    m = session_metrics(con, sid) if sid else {}
    con.close()
    rec = dict(tag=tag, model_arg=model_arg, cwd=cwd, sid=sid, wall_s=round(wall, 1),
               rc=rc, tail=tail, err=err, metrics=m, n_new=len(news))
    with OUT.open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"{tag:16} sid={sid} wall={wall:.0f}s rc={rc} in={m.get('input')} "
          f"cr={m.get('cache_read')} out={m.get('output')} tools={m.get('tools')}", flush=True)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which == "all" and OUT.exists():
        OUT.unlink()
    for pair, legs in PAIRS.items():
        if which not in ("all", pair, "naive", "greedy"):
            continue
        for name, mid in MODELS.items():
            if which in ("all", pair, "naive"):
                run_one(f"{pair}-naive-{name}", mid, legs["naive"], NAIVE_DIR)
            if which in ("all", pair, "greedy"):
                run_one(f"{pair}-greedy-{name}", mid, legs["greedy"], WORKSHOP)


if __name__ == "__main__":
    main()
