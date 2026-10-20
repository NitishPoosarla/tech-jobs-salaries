"""08-technology-jobs — 01_analysis.py

AI/tech labor-market analytics: pay by role, geography, experience, remote-ability,
and the work-type premium/discount.

Outputs: processed data, kpis.json, segments, charts.
"""
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

_shared_root = Path(__file__).resolve().parent
while _shared_root != _shared_root.parent and not (_shared_root / "shared").is_dir():
    _shared_root = _shared_root.parent
sys.path.insert(0, str(_shared_root))  # callable from repo root or standalone checkout
from shared.utils import mpl_setup, save_png, save_json   # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "outputs"
mpl_setup()


def main() -> None:
    (PROJECT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(PROJECT / "data" / "raw" / "ds_salaries.csv")
    df["salary_usd"] = df["salary_in_usd"]
    df["remote_label"] = df["remote_ratio"].map({0: "onsite", 50: "hybrid", 100: "remote"})
    df.to_csv(PROJECT / "data" / "processed" / "salaries.csv", index=False)

    kpis = {
        "records": int(len(df)),
        "years": int(df.work_year.nunique()),
        "median_salary_usd": round(float(df.salary_usd.median()), 0),
        "exp_impact": round(float(
            df[df.experience_level == "SE"].salary_usd.median() / df[df.experience_level == "EN"].salary_usd.median()), 2),
        "remote_median": round(float(df[df.remote_label == "remote"].salary_usd.median()), 0),
        "onsite_median": round(float(df[df.remote_label == "onsite"].salary_usd.median()), 0),
        "top_market": "", "top_gap_pct": 0.0, "us_row": {},
    }
    # geography: median by company_location (top 10 by records)
    geo = df.groupby("company_location").salary_usd.agg(["median", "count"]).query("count>=30")
    geo = geo.sort_values("median", ascending=False)
    kpis["top_market"] = str(geo.index[0])
    us = df[df.company_location == "US"].salary_usd.median()
    for cname in geo.index[:10]:
        row = {"median": float(geo.loc[cname, "median"]), "records": int(geo.loc[cname, "count"])}
        if cname == "US":
            kpis["us_row"] = {"median": round(float(us)), "records": int(geo.loc[cname, "count"])}
    web = df.groupby("company_location").salary_usd.agg(["median", "count"]).query("count>=30").round(0)
    web.sort_values("median", ascending=False).to_csv(OUT / "seg_geo.csv")

    role = df.groupby("job_title").salary_usd.agg(["median", "count"]).query("count>=10").sort_values("median")
    role.round(0).to_csv(OUT / "seg_roles.csv")

    yr = df.groupby("work_year").salary_usd.median().round(0)
    yr.to_csv(OUT / "seg_year.csv")

    kpis["top_role"] = str(role.index[-1])
    kpis["role_spread_pct"] = round(float(role["median"].max() / role["median"].min()), 2)
    save_json(kpis, OUT / "kpis.json")

    yr_df = yr.reset_index(); yr_df.columns = ["year", "median_usd"]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.plot(yr_df.year, yr_df.median_usd, marker="o", color="#0e7490")
    for y, v in zip(yr_df.year, yr_df.median_usd):
        ax.annotate(f"${v:,.0f}", (y, v), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
    ax.set_ylabel("Median salary (USD)"); ax.set_title("Median AI/data salary trajectory")
    save_png(fig, OUT / "charts" / "salary_trend.png")

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    top = geo.head(10)
    ax.barh(top.index, top["median"], color="#134e5e")
    ax.set_xlabel("Median salary (USD)")
    ax.set_title("Geography arbitrage — median pay by company market")
    save_png(fig, OUT / "charts" / "geo.png")

    rl = role.tail(12)
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.barh(rl.index, rl["median"], color="#d97706")
    ax.set_xlabel("Median salary (USD)")
    ax.set_title("Role ladder — medians for roles with n≥10")
    save_png(fig, OUT / "charts" / "roles.png")
    print(json.dumps(kpis, indent=2))


if __name__ == "__main__":
    main()
