# Netflix Content-Based Recommender – Findings

Data: `prepared_data.parquet` (5,915 titles). The file has **no plot description or cast column**, so the model is built from metadata only.

## Method (follows the task workflow)
1. **Features:** genres (`listed_in`), directors, countries, rating, type, release decade.
2. **Preprocessing:** every value becomes one lowercase token with a prefix (`g_`, `d_`, `c_`, `r_`, `t_`, `y_`). Multi-word names stay as a single token (`d_martinscorsese`), so "Martin Scorsese" never matches "Martin Lawrence", and "Action & Adventure" becomes `g_actionadventure`. Genres are repeated 3×, directors 2×, so genre agreement drives similarity most.
3. **Similarity:** TF-IDF on those tokens (4,876 features) and cosine similarity (5,915 × 5,915 matrix). TF-IDF down-weights very common tokens like `t_movie` or `r_tvma`.
4. **Recommendations:** `recommend(title, k)` returns the k most similar titles (never the title itself) with similarity score, genres, country, rating and year. Examples are in `output/sample_recommendations.md`.
5. **Evaluation:** there is no user/watch data, so quality is measured with proxy metrics on 1,000 random titles, top-10 lists.

| Model | Genre Jaccard@10 | Genre hit-rate@10 | Same-type rate@10 | Catalogue coverage |
|---|---|---|---|---|
| Random baseline | 0.148 | 0.391 | 0.932 | 0.825 |
| Full model (with genres) | 0.877 | 0.982 | 0.997 | 0.513 |
| Held-out (genres removed from features) | 0.337 | 0.630 | 0.977 | 0.401 |

## How to read the results
- The full model's genre scores are high partly because genres are an input, so that row shows consistency rather than proof of quality.
- The **held-out** row is the fairer test: without genres, director, country, rating, type and era still recover a same-genre title 63% of the time (random: 39%) with more than double the genre overlap (0.34 vs 0.15).
- Same-type rate for random is already 93% only because 96% of this file is movies.
- Coverage: the full model surfaces about half the catalogue across 1,000 lists; popular genre/director clusters get recommended often.

## Sample behaviour
- *Midnight Mass* → Goedam, Hemlock Grove, GHOUL (TV horror/mystery, TV-MA).
- *Ganglands* → Nowhere Man, Dealer, Arrow, Gotham (crime/action TV).
- *Sherlock Holmes* → Lock, Stock and Two Smoking Barrels (same director, Guy Ritchie, plus same genres).
- *Kung Fu Panda* → The Little Prince (same director, Mark Osborne) then family comedies.

## Limitations and next steps
- Metadata only: no synopsis, cast or viewing history. Adding descriptions (TF-IDF on text) or cast would improve relevance a lot.
- Only 219 TV shows, so TV recommendations draw from a small pool.
- Titles missing from the file (e.g. Narcos) raise a `KeyError` that suggests close matches.
- Proxy metrics can't replace user feedback; real quality needs click/watch data or human judging.
