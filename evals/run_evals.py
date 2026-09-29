#!/usr/bin/env python3
"""Run evals/evals.json with and without the plugin, then grade the answers.

For every eval and every config (with_skill, baseline) this starts an isolated
headless `claude -p` session, records the answer plus which skills and
reference files the agent used, then asks a separate judge session to check each
assertion and each must_not. Results go to evals/results/<timestamp>/.

    python3 evals/run_evals.py                  # all evals, both configs
    python3 evals/run_evals.py --only 0,3,7     # a subset
    python3 evals/run_evals.py --model sonnet --workers 4
"""
import argparse
import concurrent.futures as cf
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "qurantech"
ISOLATION = ["--setting-sources", "", "--strict-mcp-config", "--no-session-persistence"]
TOOLS = "Read Write Edit Glob Grep"


def run_claude(args, cwd, timeout):
    return subprocess.run(["claude", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout)


def generate(ev, config, model, out_dir, timeout):
    work = pathlib.Path(tempfile.mkdtemp(prefix=f"eval{ev['id']}-{config}-"))
    args = ["-p", ev["prompt"], "--model", model, "--output-format", "stream-json", "--verbose",
            "--permission-mode", "acceptEdits", "--allowedTools", *TOOLS.split(), *ISOLATION]
    if config == "with_skill":
        args += ["--plugin-dir", str(PLUGIN), "--add-dir", str(PLUGIN)]
    else:
        args += ["--disable-slash-commands"]
    started = time.time()
    try:
        proc = run_claude(args, work, timeout)
        stdout = proc.stdout
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
    skills, reads, final, cost = [], [], "", None
    for line in stdout.splitlines():
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if msg.get("type") == "assistant":
            for block in msg.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    inp = block.get("input", {})
                    if block.get("name") == "Skill":
                        skills.append(inp.get("skill"))
                    elif block.get("name") == "Read":
                        reads.append(inp.get("file_path", ""))
        elif msg.get("type") == "result":
            final = msg.get("result", "") or ""
            cost = msg.get("total_cost_usd")
    files = {}
    for path in sorted(work.rglob("*")):
        if path.is_file() and path.suffix in {".md", ".txt", ".sql", ".json", ".html", ".js", ".ts", ".py"}:
            files[str(path.relative_to(work))] = path.read_text(errors="replace")
    answer = "\n\n".join(f"### FILE {name}\n{text}" for name, text in files.items())
    answer += f"\n\n### FINAL MESSAGE\n{final}"
    refs = sorted({pathlib.Path(p).name for p in reads if "/plugins/qurantech/" in p})
    record = {"id": ev["id"], "name": ev["name"], "config": config, "seconds": round(time.time() - started),
              "cost_usd": cost, "skills_invoked": sorted({s for s in skills if s}),
              "references_read": refs, "files": list(files), "answer": answer}
    (out_dir / f"{ev['id']:02d}-{config}.answer.md").write_text(answer)
    return record


JUDGE = """You are grading an AI agent's answer against checks. Be strict: mark a check as passing only when the answer clearly satisfies it, and quote or cite the evidence. Do not reward length.

TASK GIVEN TO THE AGENT:
{prompt}

CHECKS:
{checks}

For "assert" checks, pass=true means the answer satisfies it. For "must_not" checks, pass=true means the answer does NOT do the forbidden thing (a violation is pass=false).

ANSWER:
<<<
{answer}
>>>

Reply with ONLY JSON, no code fence: {{"results":[{{"i":<check number>,"pass":true|false,"evidence":"<one short sentence>"}}]}}"""


def grade(ev, record, model, timeout):
    checks = [("assert", t) for t in ev.get("assertions", [])] + [("must_not", t) for t in ev.get("must_not", [])]
    listing = "\n".join(f"{i}. [{kind}] {text}" for i, (kind, text) in enumerate(checks))
    prompt = JUDGE.format(prompt=ev["prompt"], checks=listing, answer=record["answer"][:60000])
    args = ["-p", prompt, "--model", model, "--output-format", "json", "--disable-slash-commands", *ISOLATION]
    parsed = None
    for _ in range(2):
        try:
            proc = run_claude(args, tempfile.gettempdir(), timeout)
            text = json.loads(proc.stdout).get("result", "")
            match = re.search(r"\{.*\}", text, re.S)
            parsed = json.loads(match.group(0))
            break
        except (ValueError, subprocess.TimeoutExpired, AttributeError):
            continue
    by_index = {r["i"]: r for r in (parsed or {}).get("results", [])}
    graded = []
    for i, (kind, text) in enumerate(checks):
        r = by_index.get(i)
        graded.append({"kind": kind, "check": text, "pass": (r or {}).get("pass"),
                       "evidence": (r or {}).get("evidence", "judge returned nothing")})
    return graded


def score(graded):
    known = [g for g in graded if g["pass"] is not None]
    return (sum(1 for g in known if g["pass"]), len(graded))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated eval ids")
    ap.add_argument("--configs", default="with_skill,baseline")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--judge-model", default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--out", default=None)
    opts = ap.parse_args()

    evals = json.loads((ROOT / "evals" / "evals.json").read_text())["evals"]
    if opts.only:
        wanted = {int(x) for x in opts.only.split(",")}
        evals = [e for e in evals if e["id"] in wanted]
    configs = opts.configs.split(",")
    out_dir = pathlib.Path(opts.out) if opts.out else ROOT / "evals" / "results" / time.strftime("%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    judge_model = opts.judge_model or opts.model

    def job(pair):
        ev, config = pair
        record = generate(ev, config, opts.model, out_dir, opts.timeout)
        record["graded"] = grade(ev, record, judge_model, opts.timeout)
        record["category"] = ev.get("category")
        record["expects_skills"] = ev.get("expects_skills", [])
        print(f"[{ev['id']:>2} {config:<10}] {score(record['graded'])[0]}/{score(record['graded'])[1]} "
              f"skills={record['skills_invoked']} {record['seconds']}s", flush=True)
        return record

    jobs = [(e, c) for e in evals for c in configs]
    with cf.ThreadPoolExecutor(max_workers=opts.workers) as pool:
        records = list(pool.map(job, jobs))

    for r in records:
        r.pop("answer", None)
    (out_dir / "results.json").write_text(json.dumps(records, indent=2, ensure_ascii=False))
    write_summary(records, evals, configs, out_dir, opts)
    print(f"\nWrote {out_dir}/summary.md")


def write_summary(records, evals, configs, out_dir, opts):
    def totals(config):
        rows = [r for r in records if r["config"] == config]
        passed = sum(score(r["graded"])[0] for r in rows)
        total = sum(score(r["graded"])[1] for r in rows)
        return passed, total
    lines = [f"# Eval results ({time.strftime('%Y-%m-%d')}, model {opts.model})", "",
             "| config | checks passed |", "|---|---|"]
    for c in configs:
        p, t = totals(c)
        lines.append(f"| {c} | {p}/{t} ({round(100 * p / t) if t else 0}%) |")
    lines += ["", "| eval | category | " + " | ".join(configs) + " | skills invoked (with_skill) | expected |", "|---|---|" + "---|" * len(configs) + "---|---|"]
    for ev in evals:
        cells = []
        for c in configs:
            r = next((x for x in records if x["id"] == ev["id"] and x["config"] == c), None)
            cells.append("-" if not r else "{}/{}".format(*score(r["graded"])))
        ws = next((x for x in records if x["id"] == ev["id"] and x["config"] == "with_skill"), None)
        used = ", ".join(ws["skills_invoked"]) if ws else "-"
        lines.append(f"| {ev['id']} {ev['name']} | {ev.get('category','')} | " + " | ".join(cells) +
                     f" | {used or 'none'} | {', '.join(ev.get('expects_skills', []))} |")
    lines += ["", "## Failed checks", ""]
    for r in records:
        fails = [g for g in r["graded"] if g["pass"] is False or g["pass"] is None]
        if fails:
            lines.append(f"### {r['id']} {r['name']} ({r['config']})")
            for g in fails:
                mark = "UNGRADED" if g["pass"] is None else "FAIL"
                lines.append(f"- {mark} [{g['kind']}] {g['check']} — {g['evidence']}")
            lines.append("")
    (out_dir / "summary.md").write_text("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
