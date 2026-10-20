"""Figures for the written report (same data and rounding as the dashboard)."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

src = '../prepared_data.parquet'
out = '../report_figures'
df = pd.read_parquet(src)
df["type"] = df["type"].astype(str)
df["ya"] = df["date_added"].dt.year
df["genres"] = df["listed_in"].apply(lambda a: [g.strip() for g in a])
BLUE, ORANGE, INK, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#e1e0d9"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": "#c3c2b7", "text.color": "#52514e",
                     "axes.labelcolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e"})

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1, 1.1]})
yrs = list(range(2015, 2022))
mv = [((df.ya == y) & (df.type == "Movie")).sum() for y in yrs]
tv = [((df.ya == y) & (df.type == "TV Show")).sum() for y in yrs]
a1.bar(yrs, mv, width=.6, color=BLUE, label="Movies")
a1.bar(yrs, tv, width=.6, bottom=[m + .0 for m in mv], color=ORANGE, label="TV shows")
for y, m, t in zip(yrs, mv, tv):
    if y in (2016, 2019, 2021):
        a1.text(y, m + t + 25, f"{m + t:,}", ha="center", fontsize=9)
a1.set_title("Titles added per year", loc="left", fontsize=11, color=INK, fontweight="bold")
a1.set_ylim(0, 1600); a1.yaxis.grid(True, color=GRID); a1.set_axisbelow(True)
a1.text(2021, -230, "2021: to 25 Sep", ha="center", fontsize=8)
a1.legend(frameon=False, loc="upper left")
for s in ("top", "right"): a1.spines[s].set_visible(False)

ex = df.explode("genres")
early, late = df.ya <= 2017, df.ya >= 2020
sh = lambda g, m: round(ex[(ex.genres == g) & m].shape[0] / m.sum() * 100, 1)
names = ex.genres.value_counts()
names = names[names >= 40].index
rows = sorted(((g, round(sh(g, late) - sh(g, early), 1)) for g in names), key=lambda r: r[1])
pick = rows[:6] + rows[-6:]
pick = sorted({g: v for g, v in pick}.items(), key=lambda r: r[1])
a2.barh([g for g, _ in pick], [v for _, v in pick], height=.6,
        color=[BLUE if v >= 0 else ORANGE for _, v in pick])
for i, (g, v) in enumerate(pick):
    a2.text(v + (0.4 if v >= 0 else -0.4), i, f"{v:+.1f}", va="center", ha="left" if v >= 0 else "right", fontsize=9)
a2.axvline(0, color="#c3c2b7", lw=1)
a2.set_xlim(-20, 14)
a2.set_title("Genre share: up to 2017 vs 2020-21 (points)", loc="left", fontsize=11, color=INK, fontweight="bold")
for s in ("top", "right"): a2.spines[s].set_visible(False)
plt.tight_layout()
plt.savefig(f"{out}/fig1_portfolio.png", dpi=170)
print(pick)
