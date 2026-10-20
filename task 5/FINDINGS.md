# Netflix Classification Model – Findings

Data: `prepared_data.parquet`, 5,915 titles. The slide doesn't name a label, so two classification tasks were built.

- **Task A (main): audience level.** Predict Adult / Teen / Family from content metadata. Labels come from the rating: Adult = TV-MA, R, NC-17; Teen = TV-14, PG-13; Family = TV-PG, PG, TV-G, G, TV-Y, TV-Y7(-FV). Unrated NR/UR titles (78) are dropped, leaving 5,837 titles: 2,818 Adult, 1,854 Teen, 1,165 Family.
- **Task B (secondary): Movie vs TV Show.** Only 219 titles are TV shows (3.7%), so this is heavily imbalanced.

## Step 1 – Features
- Task A (58 features): 28 genre flags (genres with ≥20 titles), top-20 countries + "Other", release year, year added, month added, years between release and addition, runtime (minutes), seasons, TV flag, number of genres, number of directors.
- Task B (27 features): the same but **without duration and without genres**. The raw duration unit ("min" vs "Season") alone classifies Movie/TV with 100% accuracy, and genre names like "TV Dramas" give it away too, so including them would make the model look perfect without learning anything.
- The rating is never a feature in Task A.

## Step 2 – Split
80/20 stratified split (random_state 42): Task A 4,669 train / 1,168 test; Task B 4,732 / 1,183. All tuning uses 5-fold cross-validation on the training set only. The test set was used once, for the final scores, and the best model is chosen by cross-validation, not by test score.

## Steps 3–5 – Models, evaluation, comparison

**Task A – audience level** (test set; chance-level baselines for reference)

| Model | CV macro-F1 | Test accuracy | Test macro-F1 |
|---|---|---|---|
| Baseline: majority class | – | 0.483 | 0.217 |
| Baseline: random | – | 0.390 | 0.344 |
| Logistic Regression | 0.644 | 0.652 | 0.643 |
| Decision Tree | 0.619 | 0.646 | 0.639 |
| **Random Forest (selected)** | **0.655** | **0.676** | **0.668** |
| Gradient Boosting | 0.647 | 0.664 | 0.656 |

- All four models clearly beat the baselines (macro-F1 0.64–0.67 vs 0.22 for always predicting Adult).
- The models are close to each other. With 1,168 test titles, a gap of 1–3 accuracy points is within noise, so the ranking among Random Forest, Gradient Boosting and Logistic Regression is not conclusive.
- Random Forest by class: Adult F1 0.73, Family F1 0.69, **Teen F1 0.58** (precision 0.57, recall 0.60). Teen is the hardest class: 35% of Teen titles are predicted Adult and 20% of Adult titles are predicted Teen (`charts/audience_confusion_matrix.png`).

**What drives the predictions**
- Removing feature groups (5-fold CV macro-F1 of the Random Forest, 0.655 with everything): **genres −0.126**, country −0.018, runtime/type −0.012, dates −0.003, counts −0.004. Genre is by far the most useful signal.
- Top individual features by permutation importance: the "Children & Family Movies" genre (macro-F1 drops 0.129 when shuffled), runtime (0.041) and country = India (0.032).

**Task B – Movie vs TV Show** (without duration and genres; 44 TV shows in the test set)

| Model | CV avg. precision | Test ROC-AUC | Test PR-AUC | TV Show F1 |
|---|---|---|---|---|
| Baseline (always Movie) | – | 0.500 | 0.037 | 0.000 |
| Logistic Regression | 0.137 | 0.770 | 0.137 | 0.139 |
| Decision Tree | 0.160 | 0.688 | 0.159 | 0.176 |
| Random Forest | 0.171 | 0.783 | 0.204 | 0.234 |
| **Gradient Boosting (selected by CV)** | **0.207** | 0.774 | 0.209 | 0.159 |

- Models rank TV shows well above chance (ROC-AUC ~0.77, PR-AUC 0.20 vs 0.037 prevalence), but precision is low: the selected model finds 57% of TV shows with 9% precision.
- Accuracy (0.78 for the selected model) is below the "always Movie" baseline (0.96) because the models use balanced class weights to find the rare class. Accuracy is the wrong metric here, which is why PR-AUC and TV-Show F1 are reported.
- With only 44 test TV shows these numbers are noisy; the model ranking should not be trusted.

## Conclusions
1. Audience level is predictable from metadata to about 67% accuracy (3 classes), well above chance, mainly from genre. It is not very precise: Teen vs Adult is often confused, which is expected because the Teen/Adult boundary (TV-14 vs TV-MA, PG-13 vs R) is subjective.
2. Random Forest is the recommended model (best cross-validated and test score), but simple Logistic Regression is nearly as good, so the extra complexity buys little.
3. Movie vs TV Show can be separated only through leakage-prone columns (duration, genre names). Without them it is a weak classifier, so it should not be presented as a high-accuracy result.
4. Limits: no plot or cast text, a single random split, and small classes. Adding synopsis text (TF-IDF) would likely help most.

## Reproduce
`python classifier.py <parquet> output` (about 2 minutes on 2 cores). Charts are in `output/charts/`, tables in `output/*.csv`.
