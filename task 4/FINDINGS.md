# Netflix Trend Prediction – Findings

Data: `prepared_data.parquet`, 5,915 titles. The series is **titles per release year**. The file ends 2021-09-25, so 2021 is incomplete: it is shown on the charts but kept out of model training and testing. Models use complete years 2000–2020.

## Step 1 – Prepare release-year data
- Counted titles per `release_year` and filled missing years with 0. Pre-2000 years are tiny and sparse (319 titles before 1995), so modelling starts in 2000.
- 2021 has 219 titles so far (partial year).

## Step 2 – Yearly trends
- Growth from 33 titles in 2000 to a **peak of 744 in 2017**, about 20% a year compounded.
- Since the peak, the count has fallen: 730 (2018), 598 (2019, −18%), 503 (2020, −16%). That is about −12% a year from 2017 to 2020.
- Most of the catalogue is movies (96%), so the total follows the movie trend; TV shows are too few to forecast separately (`charts/03_movies_vs_tv.png`).

## Step 3 – Forecasting models and backtest
Seven models were tested with a rolling-origin backtest: train through year *t*, forecast the next 1–3 years, compare with actuals (origins 2012–2019). RMSE is in titles per year, lower is better.

| Model | RMSE, 1 yr ahead | RMSE, 3 yrs ahead | RMSE, all horizons |
|---|---|---|---|
| Naive (last value) | 124 | 325 | **234** |
| Linear trend (10 yr) | 201 | 315 | 260 |
| 3-yr moving average | 203 | 359 | 282 |
| ARIMA(1,1,1) | **112** | 453 | 297 |
| Damped Holt | 115 | 470 | 306 |
| Holt (additive trend) | 131 | 483 | 323 |
| Log-linear trend (10 yr) | 272 | 374 | 333 |

- **Best overall: Naive** ("next year equals this year"). **Best one year ahead: ARIMA(1,1,1)**, with Damped Holt close behind.
- No model forecasts 3 years ahead well (RMSE 315–483 on a series that moves 100–250 a year). The backtest window includes the 2016–2017 boom and the 2018–2020 decline, and no model anticipated the turn.
- The trend models that extrapolate growth (linear, log-linear, Holt) did worst at short range, because growth had already stopped.

## Step 4 – Forecast (`charts/05_forecast.png`, `output/forecast_all_models.csv`)

| Year | Naive | ARIMA(1,1,1) (80% interval) | Linear trend |
|---|---|---|---|
| 2021 | 503 | 461 (387–535) | 789 |
| 2022 | 503 | 442 (289–595) | 852 |
| 2023 | 503 | 433 (210–655) | 915 |
| 2024 | 503 | 428 (146–711) | 978 |
| 2025 | 503 | 427 (92–761) | 1,042 |

## Step 5 – Interpretation
1. **Growth has stalled and reversed in this data.** Content by release year rose steeply to 2017 and has declined since. The linear-trend line (rising to ~1,000) contradicts the last three years and should not be used.
2. **Best estimate: flat to slightly declining.** Next-year forecasts are about 460–500 titles; ARIMA drifts to ~430 and naive stays at 503. The intervals widen quickly, so anything beyond 1–2 years is a scenario, not a prediction.
3. **2021 will come in well below the forecasts.** 219 titles are recorded through September, and the data cutoff means the full year can't be observed here. This is a limit of the data, not evidence for or against a model.
4. **What the series measures.** It counts titles in this catalogue snapshot by release year, not Netflix's real production volume. Older titles that were removed, and recent titles not yet added, both change the shape, so the decline may partly reflect how the dataset was built.
5. **Small sample.** There are 21 years and 21 backtest points per model, so the ranking between close models (ARIMA vs Damped Holt, 112 vs 115) is not meaningful.

## Reproduce
`python trend_forecast.py <parquet> output` writes charts to `output/charts/` and tables to `output/*.csv`.
