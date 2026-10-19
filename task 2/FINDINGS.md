# Netflix EDA – Summary of Findings

Dataset: `prepared_data.parquet` – 5,915 titles × 10 columns (no missing values, no duplicate `show_id`; 2 repeated titles).

## Step 1 – Structure & statistics
- Columns: `show_id, type, title, director, country, date_added, release_year, rating, duration, listed_in`.
- `director` and `listed_in` are stored as arrays (multi-valued), so they were exploded before counting.
- Movie runtime: median 99 min, mean 101, range 3–253 min.
- TV shows: 171 of 219 (78%) have only 1 season; the longest has 15.
- Release years span 1942–2021 (median 2016); 65% of titles were released in 2015 or later.

## Step 2 – Content by type
- Movies 5,696 (96.3%) vs TV Shows 219 (3.7%). This file is heavily movie-skewed, so TV-show conclusions rest on a small sample.

## Step 3 – Top countries & categories
- Countries: United States 2,401 (40.6%), India 975 (16.5%), United Kingdom 406, Canada 189, France 156. The top 3 make up 64% of the catalogue.
- Genres: International Movies 2,558, Dramas 2,330, Comedies 1,593, Action & Adventure 815, Documentaries 762.
- Ratings: TV-MA 2,029 and TV-14 1,368 together are 57% of titles – the catalogue is aimed at mature/teen audiences.
- Directors: Rajiv Chilaka (22), Jan Suter (21), Alastair Fothergill and Raúl Campos (19 each) lead; no director dominates.

## Step 4 – Trends (see `charts/`)
- Additions grew rapidly from 2016 (243) to a peak in 2019 (1,385), then 1,277 in 2020 and 881 in 2021. 2017–2020 account for 79% of all additions. The 2021 drop probably reflects the data ending in September 2021, not a real decline.
- Additions are fairly even across months; February is lowest (380), others sit around 420–535.
- Rating mix differs by country: India is 56% TV-14, while France (52%), Canada (33%) and the UK (31%) lean TV-MA; the US and UK have a notable share of R-rated titles (~22%).

## Step 5 – Key takeaways
1. Netflix's catalogue here is overwhelmingly movies, led by the US and India.
2. Drama, comedy and International Movies are the dominant categories.
3. Content volume added peaked in 2019; most titles were released recently (median 2016).
4. Content is mature-leaning, with clear country-level differences in rating profile.
5. Caveats: the file is a prepared subset (few TV shows), and 2021 is a partial year.
