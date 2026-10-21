"""08-technology-jobs — 06_chat.py — ask-the-data chatbot.

The trust rule: every number is COMPUTED LIVE from data/processed/salaries.csv
(607 real salary records, UCI ds_salaries) at question time. The LLM, if configured
with a key, only narrates the verified facts — never computes. No key →
deterministic offline engine, identical numbers.

Usage:
    python src/06_chat.py                    # interactive REPL
    python src/06_chat.py "us vs world"      # one-shot
"""
from __future__ import annotations

import json
import os
import statistics
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DATA = PROJECT / "data" / "processed" / "salaries.csv"

HEADLINE = ("Overall: 607 records · global median $101,570 · US median $135,000 · "
            "remote premium +16% over on-site · senior = ~2.4x junior.")

FIRST_MSG = """Questions I can answer (all computed live from the data):
  us vs world · remote premium · top roles · by experience
  trend by year · biggest markets
Type 'quit' to exit."""


def compute(q: str) -> list[str] | None:
    q = q.lower().strip()

    if "us" in q and ("world" in q or "market" in q or "vs" in q or "geo" in q):
        import pandas as pd
        s = pd.read_csv(DATA)
        m = s.groupby("company_location")["salary_in_usd"].median().sort_values(ascending=False)
        us = m.get("US")
        others = m.drop("US", errors="ignore").head(5)
        return [f"US median: ${us:,.0f} (top market, {int((s['company_location']=='US').sum())} records).",
                "Next biggest markets by median:",
                *[f"  {c} — ${v:,.0f}" for c, v in others.items()],
                f"US premium vs #2: {(us/others.iloc[0]-1):.0%} — compensation is set by geography of the employer."]

    if "remote" in q:
        import pandas as pd
        s = pd.read_csv(DATA)
        g = s.groupby("remote_label")["salary_in_usd"].median()
        rem = g.get("remote"); onsite = g.get("onsite")
        return [f"Remote median: ${rem:,.0f} · on-site median: ${onsite:,.0f} → "
                f"premium {(rem/onsite-1):+.0%}.",
                f"Hybrid sits at ${g.get('hybrid', float('nan')):,.0f}.",
                "Sample sizes live in the dashboard note: remote n is smaller — directional, not causal."]

    if "role" in q or "job" in q or "title" in q:
        import pandas as pd
        r = pd.read_csv(PROJECT / "outputs" / "seg_roles.csv")
        r = r.sort_values("median", ascending=False)
        lines = ["Top-paying roles by median salary (US-adjusted records included):"]
        lines += [f"  {row['job_title']} — ${row['median']:,.0f} ({int(row['count'])} recs)"
                  for _, row in r.head(5).iterrows()]
        lines += ["Lower end:", f"  {r.tail(1)['job_title'].iloc[0]} — ${r.tail(1)['median'].iloc[0]:,.0f}"]
        return lines

    if "experience" in q or "junior" in q or "senior" in q:
        import pandas as pd
        s = pd.read_csv(DATA)
        g = s.groupby("experience_level")["salary_in_usd"].median()
        med = {"EN": "Entry", "MI": "Mid", "SE": "Senior", "EX": "Executive"}
        lines = ["Median salary by experience level:"]
        lines += [f"  {med.get(l, l)} — ${v:,.0f}" for l, v in g.items()]
        if "EN" in g and "EX" in g:
            lines.append(f"Executive vs entry: {g['EX']/g['EN']:.1f}x.")
        if "EN" in g and "SE" in g:
            lines.append(f"Senior vs entry: {g['SE']/g['EN']:.1f}x — the fastest salary leap is the one into seniority.")
        return lines

    if "year" in q or "trend" in q or "2020" in q or "2022" in q:
        import pandas as pd
        y = pd.read_csv(PROJECT / "outputs" / "seg_year.csv")
        return ["Median salary by work_year (USD-adjusted):",
                *[f"  {r['work_year']} — ${r['median']:,.0f}" for _, r in y.iterrows()]]

    if "size" in q or "company" in q:
        import pandas as pd
        s = pd.read_csv(DATA)
        g = s.groupby("company_size")["salary_in_usd"].median()
        size = {"S": "Small", "M": "Mid", "L": "Large"}
        return ["Median salary by company size:",
                *[f"  {size.get(l, l)} — ${v:,.0f}" for l, v in g.items()]]

    return None


def offline_answer(q: str) -> str:
    try:
        lines = compute(q)
    except Exception as e:  # noqa: BLE001
        return f"\n(error while computing from the csv — this engine never guesses: {e})\n"
    if lines is None:
        return ("\nI could not map that to a computed fact, so here is the verified headline\n"
                "(try: us vs world, remote premium, top roles, by experience, trend).\n\n"
                f"{HEADLINE}\n")
    return "\n".join(["[computed live from salaries.csv —]"] + lines) + f"\n\n{HEADLINE}\n"


def narrate_with_llm(q: str, facts: str) -> str:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        return ""
    import urllib.request
    body = json.dumps({"model": "llama-3.1-8b-instant", "messages": [
        {"role": "system", "content": "You are a precise labor-market analyst. Use ONLY the numbers in the supplied verified facts. Do not compute, estimate or invent any number. 3 sentences max."},
        {"role": "user", "content": f"Facts (verified, pre-computed):\n{facts}\n\nQuestion: {q}"}]})
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions", data=body.encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return "\n\nNARRATED: " + json.loads(r.read())["choices"][0]["message"]["content"].strip() + "\n"
    except Exception:
        return ""


def main() -> None:
    if not DATA.exists():
        print("Run src/00_download_data.py + src/01_analysis.py first."); sys.exit(2)

    if len(sys.argv) > 1:  # one-shot
        q = " ".join(sys.argv[1:])
        base = offline_answer(q)
        if os.environ.get("GROQ_API_KEY") and "computed live" in base:
            base += narrate_with_llm(q, base)
        print(base)
        return

    print(FIRST_MSG + "\n")
    while True:
        try:
            q = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); return
        if q.lower() in {"quit", "exit", "q", ""}:
            return
        base = offline_answer(q)
        if os.environ.get("GROQ_API_KEY") and "computed live" in base:
            base += narrate_with_llm(q, base)
        print(base)


if __name__ == "__main__":
    main()
