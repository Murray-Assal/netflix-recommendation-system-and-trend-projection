# Netflix Content Strategy: Data Science Business Insights Report

Oct 20, 2026 · @Murad

## Executive summary

The catalogue in this dataset is a movie-heavy, mature-skewing library led by the US and India. Its growth has levelled off, and the clearest opportunities are in genre mix, emerging-market content, TV series and family titles.

**What the data shows**

- **Scale and mix:** 5,915 titles, 96% movies. The US supplies 41% and India 16.5%; the top three countries (US, India, UK) make up 64%.
- **Growth has peaked:** titles added per year rose from 243 in 2016 to 1,385 in 2019, then fell to 881 by September 2021. By release year, output peaked in 2017 (744) and has declined since.
- **The mix is shifting:** comedies, dramas, romance and action are a growing share of additions, while documentaries fell from 24% of titles added up to 2017 to 8% in 2020-21 and stand-up from 9% to 2.5%.
- **New markets are rising:** Nigeria, Egypt, Indonesia and the Philippines went from almost nothing to 1.8-3.1% of 2020-21 additions each, while the UK fell from 9.7% to 5.3%.
- **Models work, with limits:** the audience-level classifier predicts Adult / Teen / Family with 67.6% accuracy (48.3% for guessing the biggest class), and the recommender finds same-genre titles 63% of the time even without genre as an input (39% at random).

**What we recommend**

1. Plan for flat catalogue volume (about 430-500 titles per release year) and compete on genre mix and quality, not volume.
2. Keep shifting investment toward comedy, drama, romance and action; treat documentaries and stand-up as selective bets.
3. Scale local-language content in Nigeria, Egypt, Indonesia and the Philippines, and avoid over-reliance on a single market.
4. Grow TV series and family titles, which are under-represented (3.7% TV, about one in five rated titles for families).
5. Use the recommender to improve discovery now, and collect viewing data to replace metadata-only similarity.

These are supply-side findings: the data has no viewership, cost or revenue, so each recommendation is a hypothesis to test against performance data.

## Data and approach

All results come from one file of 5,915 Netflix titles added through 25 September 2021, with ten fields: type, title, director, country, date added, release year, rating, duration and genres. It has no missing values and no duplicate IDs. An [interactive dashboard](https://claude.ai/artifact/2EyYmgvHAz7iBfz4u9ACkT) holds every chart in this report, with filters and a table view for each.

**Preparation.** Genres and directors were split into lists. Ratings were grouped into three audience levels: Adult (TV-MA, R, NC-17), Teen (TV-14, PG-13) and Family (TV-PG, PG, TV-G, G, TV-Y, TV-Y7); 78 unrated titles are left out of audience analysis. Duration became minutes for movies and seasons for TV shows.

| Question | Method | How it was checked |
| --- | --- | --- |
| What does the catalogue look like, and how is it changing? | Counts and shares by type, country, genre, rating and year added; early (up to 2017) against recent (2020-21) periods | Shares, so growth in volume does not distort comparisons |
| How many titles will there be by release year? | Seven models on 2000-2020, including naive, trend, Holt and ARIMA | Rolling backtest: train to year t, predict the next 1-3 years |
| Can audience level be predicted? | Logistic regression, decision tree, random forest, gradient boosting on 58 features | 80/20 split, 5-fold cross-validation, comparison with guessing |
| What should a viewer watch next? | TF-IDF cosine similarity on genre, director, country, rating, type, decade | Same-genre hit rate with genre hidden, against random |

## Content portfolio analysis

The catalogue is 96% movies, 41% US-made and mature-skewing, and what gets added has moved steadily toward comedy, drama and romance.

&#91;image: Titles added per year, and genre share up to 2017 against 2020-21\]

- **Concentration:** the US supplies 2,401 titles (40.6%), India 975 (16.5%) and the UK 406 (6.9%). Canada, France and Spain follow with 140-190 each. 78 countries appear, but the top three account for 64%.
- **Genres:** International Movies (2,558), Dramas (2,330) and Comedies (1,593) lead. A title carries up to three genres.
- **Ratings:** TV-MA (2,029) and TV-14 (1,368) together cover 57% of titles. Among rated titles, Adult fell from 52% of additions up to 2017 to 46% in 2020-21 while Teen rose from 25% to 34%; Family stayed near 20%.
- **Pace of additions:** 243 titles were added in 2016, a peak of 1,385 in 2019, and 881 in 2021 through September. The years 2017-2020 account for 79% of everything in the file.
- **Genre mix, up to 2017 against 2020-21 (share of titles carrying the genre):** Comedies 20.3% to 30.9%, Dramas 32.1% to 40.9%, Romantic Movies 5.9% to 12.4% and Action & Adventure 9.7% to 15.6%. Documentaries fell from 23.8% to 7.6% and Stand-Up Comedy from 9.2% to 2.5%.
- **Country mix, same periods:** Nigeria rose from 0.3% to 3.1%, Egypt from 0% to 2.6%, Indonesia from 0.1% to 1.9% and the Philippines from 0% to 1.8%. The UK fell from 9.7% to 5.3%. India peaked at 27% of 2018 additions and settled near 14%.
- **TV:** only 219 titles (3.7%) are TV shows, but their share of each year's additions grew from 2.1% in 2018 to 5.7% in 2021.

Shares compare the mix of each period, so they are not distorted by the catalogue growing between periods.

## Predictive modelling

The models are useful but modest: the forecast is reliable for about one year, the classifier beats guessing by a wide margin without being precise, and the recommender is a sound baseline for new titles.

**Release-year forecast.** The series counts titles by release year for 2000-2020; 2021 is excluded because the data ends in September. Output peaked at 744 in 2017 and fell to 503 by 2020, about 12% a year. In a rolling backtest the "same as last year" forecast had the lowest overall error (RMSE 234 titles), ARIMA(1,1,1) was best one year ahead (112) with Damped Holt close behind (115), and every model was off by 315 or more at three years. The ARIMA forecast is 461 titles for 2021 (80% range 387-535), easing to 427 by 2025 with a range of 92-761. A 10-year linear trend, which projects about 1,040 by 2025, contradicts the last three years and should not be used. The 219 titles recorded for 2021 through September cannot test the forecast because the year is incomplete.

&#91;image: Titles by release year with forecasts to 2025 and the ARIMA 80% interval\]

**Audience-level classifier.** Four models predicted Adult, Teen or Family from genres, country, dates, runtime and counts. Random Forest was best by cross-validation: 67.6% test accuracy and 0.668 macro-F1, against 48.3% and 0.217 for always predicting Adult. The four models are within 3 points of each other, which is within test-set noise. Adult (F1 0.73) and Family (0.69) are predicted better than Teen (0.58); 35% of Teen titles are labelled Adult. Genre carries the signal: removing it cuts cross-validated macro-F1 from 0.655 to 0.529, while no other feature group costs more than 0.02. A second task, Movie vs TV Show, is weak once the giveaway columns (duration, genre names) are removed: ROC-AUC about 0.77, but the selected model's precision for TV shows is only 9%.

**Recommender.** Titles are compared by cosine similarity on genre, director, country, rating, type and release decade. With genre hidden from the model, its top 10 contains a same-genre title 63% of the time (random: 39%), and shares 0.34 genre overlap against 0.15. Examples: *Midnight Mass* returns *Goedam*, *Hemlock Grove* and *GHOUL* (TV horror and mystery); *Kung Fu Panda* returns *The Little Prince*, which shares a director (Mark Osborne).

## Business recommendations

Six actions, in the same order as the dashboard's Actions view. All are supply-side: the file has no viewing, cost or revenue figures, so each carries the test that would confirm it before money moves.

| # | Action | Evidence | Confidence | How to test it |
| --- | --- | --- | --- | --- |
| 1 | Plan for flat volume and compete on mix | Release-year output peaked at 744 in 2017, was 503 in 2020; ARIMA forecast 461 for 2021, about 427 by 2025 | Medium: backtest error is 112 titles at one year, over 300 at three | Compare each new year with the forecast range (387-535 for 2021) |
| 2 | Shift investment toward comedy, drama, romance and action | Comedies 20.3% to 30.9% of titles, Romantic Movies 5.9% to 12.4%, Action 9.7% to 15.6% (up to 2017 against 2020-21); Documentaries 23.8% to 7.6%, Stand-Up 9.2% to 2.5% | Medium: shows what was added, not what was watched | Compare viewing hours per title by genre before reallocating budget |
| 3 | Scale local-language content in rising markets | Nigeria 0.3% to 3.1% of additions, Egypt 0% to 2.6%, Indonesia 0.1% to 1.9%, Philippines 0% to 1.8%; UK down from 9.7% to 5.3% | Medium: Nigeria and Egypt have about 100 titles each | Pilot local slates and compare retention with imported titles |
| 4 | Grow TV series | TV is 3.7% of titles, but its share of additions rose from 2.1% in 2018 to 5.7% in 2021 | Low: 219 shows, no retention data | Compare series completion and return rates with films |
| 5 | Serve families deliberately | Family-rated titles are 20% of rated titles (1,165 of 5,837) against 46% Adult; Teen grew from 25% to 34% of additions | Low to medium | Check family-profile viewing against the supply of family titles |
| 6 | Use the models as helpers, not decision makers | Recommender finds a same-genre title 63% of the time without seeing genre (random 39%); classifier is right 67.6% of the time | Medium for the recommender, low for automatic rating | Use the recommender for new titles with no history; use the classifier only to flag the 78 unrated titles and rating mismatches for human review |

The largest risk is acting on supply trends as if they were demand. The first test for actions 1, 2 and 4 is the same: join this catalogue to viewing data.

## Limitations and next steps

These results describe what is in the catalogue, not what viewers choose: the file ends on 25 September 2021 and has no viewing, cost or revenue data.

**Limitations**

- **No demand data.** Every recommendation is a hypothesis about supply trends until it is checked against viewing.
- **A snapshot, not a history.** Titles removed from the catalogue are absent, 2021 is incomplete, and release-year counts are not Netflix's production volume.
- **Small groups.** Only 219 titles are TV shows and Nigeria and Egypt have about 100 titles each, so conclusions about them are rough.
- **Model scope.** The classifier uses one random split, the forecast rests on 21 yearly points, and the recommender sees only metadata, with no synopsis or cast.

**Next steps**

1. Join the catalogue to viewing data by title and re-test recommendations 2 to 5.
2. Add synopsis and cast text to the recommender and compare it with a popularity baseline in an A/B test.
3. Refresh the data past September 2021 and re-run the forecast on complete years.
4. Re-train the audience classifier with a time-based split to check it holds on newer titles.
