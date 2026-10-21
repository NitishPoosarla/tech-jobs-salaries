"""08-technology-jobs — 02_ai_market_note.py — measured AI labor-market note."""
from pathlib import Path
import csv
import json
import sys

_shared_root = Path(__file__).resolve().parent
while _shared_root != _shared_root.parent and not (_shared_root / "shared").is_dir():
    _shared_root = _shared_root.parent
sys.path.insert(0, str(_shared_root))  # callable from repo root or standalone checkout
from shared import llm   # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "outputs"


def main() -> None:
    kpis = json.loads((OUT / "kpis.json").read_text())
    with open(OUT / "seg_geo.csv") as f:
        geo = list(csv.DictReader(f))[:10]
    with open(OUT / "seg_roles.csv") as f:
        roles = list(csv.DictReader(f))[-10:]
    drivers = {
        "Geography is a big multiplier": (f"Leader market: {kpis['top_market']}; role ladder spans "
                                          f"{kpis['role_spread_pct']}x between the lowest- and highest-median roles (n≥10)."),
        "Experience premium": (f"SE medians run {kpis['exp_impact']}x EN medians — leveling, not title inflation, moves pay."),
        "Work-mode": (f"Remote median ${kpis['remote_median']:,.0f} vs onsite ${kpis['onsite_median']:,.0f}."),
    }
    prompt = f"""You are writing a career-strategy note for early/mid-career analytics professionals.
Use ONLY verified metrics. Deliver: (1) three-sentence market read, (2) 3 actions,
(3) honest caveats about sample and market timing.
Metrics: {json.dumps({**kpis, "geo": geo, "roles": roles}, indent=1)}"""
    md = llm.write_insights(str(OUT / "insights.md"), "AI/tech labor market note", kpis, drivers, prompt)
    print(md[:900])


if __name__ == "__main__":
    main()
