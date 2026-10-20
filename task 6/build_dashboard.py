"""Build the data payload and final HTML for the Netflix Content Insights dashboard.

Usage: python build_dashboard.py <parquet> <template.html> <out.html>
Reads model outputs from the sibling project folders produced in Tasks 2-5.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

src = '../prepared_data.parquet'
template = 'template.html'
out_html = 'dashboard.html'

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_parquet(src).reset_index(drop=True)
for c in ("type", "country", "rating"):
    df[c] = df[c].astype(str)


def to_list(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return []
    if isinstance(v, str):
        v = v.split(",")
    return [str(x).strip() for x in v if str(x).strip()]


df["genres"] = df["listed_in"].apply(to_list)
df["directors"] = df["director"].apply(to_list)
df["ya"] = df["date_added"].dt.year
AUD = {"TV-MA": 0, "R": 0, "NC-17": 0, "TV-14": 1, "PG-13": 1,
       "TV-PG": 2, "PG": 2, "TV-G": 2, "G": 2, "TV-Y": 2, "TV-Y7": 2, "TV-Y7-FV": 2}
df["aud"] = df["rating"].map(AUD).fillna(3).astype(int)

countries = list(df["country"].value_counts().index)
cidx = {c: i for i, c in enumerate(countries)}
genres = list(df["genres"].explode().value_counts().index)
gidx = {g: i for i, g in enumerate(genres)}
ratings = list(df["rating"].value_counts().index)
ridx = {r: i for i, r in enumerate(ratings)}
num = df["duration"].str.extract(r"(\d+)")[0].astype(float).fillna(0).astype(int)
is_tv = (df["type"] == "TV Show").astype(int)

# row: [type, country, yearAdded, releaseYear, audience(0-2, 3=unrated), minutes, seasons, rating, [genres]]
rows = [[int(is_tv[i]), cidx[df.country[i]], int(df.ya[i]), int(df.release_year[i]), int(df.aud[i]),
         0 if is_tv[i] else int(num[i]), int(num[i]) if is_tv[i] else 0, ridx[df.rating[i]],
         [gidx[g] for g in df.genres[i]]] for i in range(len(df))]

# ---- content-based recommender (same method as Task 3) -------------------
def token(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def soup(r):
    p = ["g_" + token(g) for g in r.genres] * 3
    p += ["d_" + token(d) for d in r.directors] * 2
    p += ["c_" + token(r.country), "r_" + token(r.rating), "t_" + token(r.type),
          "y_" + str(r.release_year // 10 * 10)]
    return " ".join(p)


X = TfidfVectorizer(token_pattern=r"\S+", lowercase=False).fit_transform(df.apply(soup, axis=1))
sim = linear_kernel(X, X)
np.fill_diagonal(sim, -1)
K = 10
top = np.argsort(-sim, axis=1)[:, :K]
nbr = [[v for j in top[i] for v in (int(j), int(round(sim[i, j] * 1000)))] for i in range(len(df))]
dirs = [", ".join(d[:2]) for d in df.directors]

# ---- static results from earlier tasks ----------------------------------
fc = pd.read_csv(ROOT / "netflix_forecast/output/forecast_all_models.csv")
fc.columns = ["model", "year", "forecast", "low", "high"]
trend = pd.read_csv(ROOT / "netflix_forecast/output/yearly_trend.csv")
sc_all = pd.read_csv(ROOT / "netflix_forecast/output/model_scores.csv")
sc1 = pd.read_csv(ROOT / "netflix_forecast/output/model_scores_h1.csv").set_index("model")
sc3 = pd.read_csv(ROOT / "netflix_forecast/output/model_scores_h3.csv").set_index("model")
back = [{"model": r.model, "h1": float(sc1.loc[r.model, "RMSE"]), "h3": float(sc3.loc[r.model, "RMSE"]),
         "all": float(r.RMSE)} for r in sc_all.itertuples()]
aud = pd.read_csv(ROOT / "netflix_classifier/output/results_audience.csv")
abl = pd.read_csv(ROOT / "netflix_classifier/output/ablation_audience.csv")
imp = pd.read_csv(ROOT / "netflix_classifier/output/importance_audience.csv", index_col=0).iloc[:, 0].head(10)
typ = pd.read_csv(ROOT / "netflix_classifier/output/results_type.csv")
rec_eval = pd.read_csv(ROOT / "netflix_recsys/output/evaluation.csv", index_col=0)

forecast = {m: g[["year", "forecast", "low", "high"]].round(0).astype(int).to_dict("records")
            for m, g in fc.groupby("model")}
data = {
    "snapshot": str(df["date_added"].max().date()),
    "countries": countries, "genres": genres, "ratings": ratings,
    "titles": df["title"].tolist(), "dirs": dirs, "rows": rows, "nbr": nbr,
    "history": [{"year": int(r.release_year), "n": int(r.titles)} for r in trend.itertuples()],
    "partial2021": int((df.release_year == 2021).sum()),
    "forecast": forecast, "backtest": back,
    "audience": aud.fillna(-1).to_dict("records"),
    "confusion": [[425, 115, 24], [131, 221, 19], [38, 51, 144]],
    "ablation": abl.to_dict("records"),
    "importance": [{"f": k, "v": float(v)} for k, v in imp.items()],
    "typeTask": typ.fillna(-1).to_dict("records"),
    "recEval": [{"model": k, **{c: float(v) for c, v in r.items()}} for k, r in rec_eval.iterrows()],
}

# ---- numbers quoted in the page text: assert they match the data ---------
ex = df.explode("genres")
early, late = df.ya <= 2017, df.ya >= 2020


def gshare(g, m):
    return round(float(ex[(ex.genres == g) & m].shape[0] / m.sum() * 100), 1)


def cshare(c, m):
    return round(float((df.country[m] == c).mean() * 100), 2)


facts = {
    "n": len(df), "movie_pct": round((df.type == "Movie").mean() * 100, 1),
    "us_pct": round((df.country == "United States").mean() * 100, 1),
    "india_pct": round((df.country == "India").mean() * 100, 1),
    "doc_early": gshare("Documentaries", early), "doc_late": gshare("Documentaries", late),
    "stand_early": gshare("Stand-Up Comedy", early), "stand_late": gshare("Stand-Up Comedy", late),
    "com_early": gshare("Comedies", early), "com_late": gshare("Comedies", late),
    "nigeria_late": cshare("Nigeria", late), "egypt_late": cshare("Egypt", late),
    "uk_early": cshare("United Kingdom", early), "uk_late": cshare("United Kingdom", late),
    "added_2016": int((df.ya == 2016).sum()), "added_2019": int((df.ya == 2019).sum()),
    "added_2021": int((df.ya == 2021).sum()),
    "tv_share_2018": round(float((df[df.ya == 2018].type == "TV Show").mean() * 100), 1),
    "tv_share_2021": round(float((df[df.ya == 2021].type == "TV Show").mean() * 100), 1),
}
print(json.dumps(facts, indent=1))
expect = {"n": 5915, "movie_pct": 96.3, "us_pct": 40.6, "india_pct": 16.5, "doc_early": 23.8,
          "doc_late": 7.6, "stand_early": 9.2, "stand_late": 2.5, "com_early": 20.3, "com_late": 30.9,
          "nigeria_late": 3.1, "egypt_late": 2.64, "uk_early": 9.66, "uk_late": 5.33,
          "added_2016": 243, "added_2019": 1385, "added_2021": 881,
          "tv_share_2018": 2.1, "tv_share_2021": 5.7}
bad = {k: (facts[k], v) for k, v in expect.items() if abs(facts[k] - v) > 0.06}
assert not bad, f"text numbers no longer match the data: {bad}"

html = Path(template).read_text()
payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
assert "/*__DATA__*/" in html
Path(out_html).write_text(html.replace("/*__DATA__*/", "window.DATA=" + payload + ";"))
print("wrote", out_html, f"{Path(out_html).stat().st_size/1e6:.2f} MB")
