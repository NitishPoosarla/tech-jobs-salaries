"""08-technology-jobs — 03_dashboard.py — single-file job market dashboard."""
from pathlib import Path
import json
import sys

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

_shared_root = Path(__file__).resolve().parent
while _shared_root != _shared_root.parent and not (_shared_root / "shared").is_dir():
    _shared_root = _shared_root.parent
sys.path.insert(0, str(_shared_root))  # callable from repo root or standalone checkout
from shared.dashboard import build_dashboard   # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "outputs"


def main() -> None:
    kpis = json.loads((OUT / "kpis.json").read_text())
    geo = pd.read_csv(OUT / "seg_geo.csv", index_col=0).head(12)
    roles = pd.read_csv(OUT / "seg_roles.csv", index_col=0).tail(12)
    sal = pd.read_csv(PROJECT / "data" / "processed" / "salaries.csv")

    fig_geo = go.Figure(go.Bar(y=geo.index, x=geo["median"], orientation="h", marker_color="#134e5e",
                               text=geo["median"].astype(int), textposition="outside",
                               texttemplate="$%{text:,}"))
    fig_geo.update_layout(xaxis_title="Median salary (USD)")

    fig_rol = go.Figure(go.Bar(y=roles.index, x=roles["median"], orientation="h", marker_color="#d97706"))
    fig_rol.update_layout(xaxis_title="Median salary (USD)")

    fig_exp = px.box(sal, x="experience_level", y="salary_usd", color="experience_level",
                     category_orders={"experience_level": ["EN", "MI", "SE", "EX"]})
    fig_exp.update_layout(showlegend=False, yaxis_title="Salary (USD)")

    sal_s = sal[sal.salary_usd.between(10000, 500000)]
    fig_scatter = px.scatter(sal_s.sample(min(1200, len(sal_s)), random_state=1),
                             x="work_year", y="salary_usd", color="remote_label", opacity=.6, hover_data=["job_title"])
    fig_scatter.update_layout(xaxis_title="Year", yaxis_title="Salary (USD)")

    build_dashboard(
        str(PROJECT / "dashboard" / "index.html"),
        title="AI/Tech Job Market Intelligence",
        subtitle=("Which roles & geographies are over/under paid — with honest caveats. "
                  "Public ds_salaries mirror (Kaggle 2020-2024 era), verified in Python."),
        badges=["Technology", "Comp analytics", "Geography arbitrage", "LLM narration"],
        kpis=[
            {"label": "Records", "value": f"{kpis['records']:,}", "note": f"{kpis['years']} years"},
            {"label": "Median salary", "value": f"${kpis['median_salary_usd']:,.0f}"},
            {"label": "SE/EN premium", "value": f"{kpis['exp_impact']}x"},
            {"label": "Leader market", "value": kpis["top_market"]},
            {"label": "Remote vs onsite", "value": f"${kpis['remote_median']:,.0f}",
             "note": f"onsite ${kpis['onsite_median']:,.0f}"},
            {"label": "Role spread", "value": f"{kpis['role_spread_pct']}x", "note": "n≥10 roles"},
        ],
        figures=[
            {"title": "Geography ladder", "sub": "median by company market (records≥30)", "fig": fig_geo},
            {"title": "Role ladder", "sub": "top roles with n≥10", "fig": fig_rol},
            {"title": "Experience level distribution", "fig": fig_exp},
            {"title": "Salary by year & work mode", "fig": fig_scatter},
        ],
        recommendations=[
            "Target leveling milestones, not titles: the SE→ pay step beats lateral title moves in expected value.",
            f"Skew applications toward {kpis['top_market']} team satellites or remote-first firms if relocation is off the table.",
            "Treat remote-vs-onsite medians as a menu, not a law: sample imbalance by geography nudges these numbers.",
            "For candidates: use median-of-your-level-and-market bands in negotiation — outliers mislead both sides.",
        ],
        footer=("Data: public GitHub mirror of the Kaggle ds_salaries dataset. AI narrates verified metrics "
                "only. Sample skews to certain markets/years — caveats in the insights report."),
    )
    print("dashboard written")


if __name__ == "__main__":
    main()
