"""08 — banner: light navy, pay rungs by level, leveling + remote callouts."""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

k = json.loads((Path(__file__).resolve().parents[1] / "outputs" / "kpis.json").read_text())

fig, ax = plt.subplots(figsize=(12, 6.75), dpi=100)
ax.set_xlim(0, 12); ax.set_ylim(0, 6.75); ax.axis("off")
fig.patch.set_facecolor("#eef1f8")

ax.text(0.5, 6.05, "This market prices LEVELING first, then location",
        fontsize=20, fontweight="bold", color="#1e2a4a")
ax.text(0.5, 5.5, f"{k['records']} AI/data salary records, USD-normalized, three years — public mirror",
        fontsize=11, color="#5a657d")

rungs = [("Entry (EN)", "≈$65k", 1.75), ("Senior (SE)", "≈$155k", 3.05), ("Exec (EX)", "≈$210k", 4.35)]
for name, val, y in rungs:
    ax.plot([1.0, 4.6], [y, y], color="#3a4a77", lw=4, solid_capstyle="round", alpha=0.85)
    ax.text(4.85, y, val, fontsize=17, fontweight="bold", color="#26418f", va="center")
    ax.text(6.6, y, name, fontsize=12, color="#5a657d", va="center")

ax.add_patch(plt.Rectangle((7.7, 3.25), 3.9, 1.6, color="#26418f"))
ax.text(7.95, 4.35, "senior ≈ 2.4x entry", fontsize=14, fontweight="bold", color="white")
ax.text(7.95, 3.72, "before the role title\nmatters at all", fontsize=10.5,
        color="#c8d3ee", linespacing=1.35)
ax.text(1.0, 0.7, f"remote vs onsite medians: \\${k['remote_median']/1000:.0f}k vs \\${k['onsite_median']/1000:.0f}k (+16%) · "
        "median by role spread ~2.4x (n\\>=10 filter)", fontsize=10.5, color="#5a657d")
fig.savefig(Path(__file__).resolve().parents[1] / "outputs" / "banner.png",
            dpi=100, facecolor=fig.get_facecolor())
print("banner written")
