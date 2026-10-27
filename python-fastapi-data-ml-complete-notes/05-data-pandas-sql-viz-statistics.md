# 05. Data Work, pandas, SQL, Visualization, And Statistics

## 1. Data Work Mental Model

Data work is not just coding. It is a decision process.

```mermaid
flowchart LR
  A["Question"] --> B["Data collection"]
  B --> C["Cleaning"]
  C --> D["Exploration"]
  D --> E["Model or analysis"]
  E --> F["Uncertainty"]
  F --> G["Decision"]
  G --> H["Communication"]
```

Always begin with:

- What question are we answering?
- What decision will this support?
- What data do we trust?
- What could bias the result?

## 2. pandas Core Objects

Series:

```python
import pandas as pd

prices = pd.Series([100, 200, 150], name="price")
```

DataFrame:

```python
orders = pd.DataFrame(
    {
        "order_id": [1, 2, 3],
        "user_id": [10, 20, 10],
        "amount": [500, 800, 300],
    }
)
```

Mental model:

- Series is one labeled column.
- DataFrame is a table of labeled columns.
- Index labels rows.

## 3. Reading Data

```python
df = pd.read_csv("orders.csv")
```

Useful options:

```python
df = pd.read_csv(
    "orders.csv",
    parse_dates=["created_at"],
    dtype={"user_id": "string"},
)
```

Read SQL:

```python
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg://user:password@localhost:5432/app")
orders = pd.read_sql("SELECT * FROM orders", engine)
```

## 4. Inspecting Data

```python
df.head()
df.tail()
df.info()
df.describe()
df.shape
df.columns
df.dtypes
```

Ask:

- Are columns named clearly?
- Are data types correct?
- Are there missing values?
- Are there duplicates?
- Are there impossible values?

## 5. Selecting Data

Columns:

```python
df["amount"]
df[["order_id", "amount"]]
```

Rows by label:

```python
df.loc[0:5, ["order_id", "amount"]]
```

Rows by position:

```python
df.iloc[0:5, 0:2]
```

Boolean filter:

```python
large_orders = df[df["amount"] >= 500]
```

## 6. Missing Data

Find:

```python
df.isna().sum()
```

Drop:

```python
df = df.dropna(subset=["amount"])
```

Fill:

```python
df["country"] = df["country"].fillna("Unknown")
```

Important: missingness can be informative. Ask why data is missing.

Types:

- MCAR: missing completely at random.
- MAR: missing related to observed data.
- MNAR: missing related to unobserved value itself.

## 7. GroupBy

```python
revenue_by_user = (
    df.groupby("user_id", as_index=False)
    .agg(total_revenue=("amount", "sum"), orders=("order_id", "count"))
    .sort_values("total_revenue", ascending=False)
)
```

GroupBy means split, apply, combine.

```mermaid
flowchart LR
  A["DataFrame"] --> B["Split by user"]
  B --> C["Aggregate amount"]
  C --> D["Combine result"]
```

## 8. Merge And Join

```python
orders = pd.DataFrame({"user_id": [1, 2], "amount": [100, 200]})
users = pd.DataFrame({"user_id": [1, 2], "country": ["IN", "US"]})

joined = orders.merge(users, on="user_id", how="left")
```

Join types:

- `inner`: only matching rows.
- `left`: keep all left rows.
- `right`: keep all right rows.
- `outer`: keep all rows from both.

## 9. Reshaping

Wide to long:

```python
long = df.melt(
    id_vars=["user_id"],
    value_vars=["jan_sales", "feb_sales"],
    var_name="month",
    value_name="sales",
)
```

Pivot:

```python
wide = long.pivot_table(
    index="user_id",
    columns="month",
    values="sales",
    aggfunc="sum",
)
```

## 10. Time-Series Handling

```python
df["created_at"] = pd.to_datetime(df["created_at"])
df = df.set_index("created_at").sort_index()
```

Resample:

```python
daily_revenue = df["amount"].resample("D").sum()
weekly_revenue = df["amount"].resample("W").sum()
```

Rolling average:

```python
daily_revenue.rolling(window=7).mean()
```

Time-series gotchas:

- Time zones.
- Missing dates.
- Duplicate timestamps.
- Leakage from future data.
- Seasonality.
- Holidays.

## 11. Advanced pandas Performance

Prefer vectorization:

```python
df["tax"] = df["amount"] * 0.18
```

Avoid row loops:

```python
for index, row in df.iterrows():
    ...
```

Memory tips:

```python
df["category"] = df["category"].astype("category")
df["small_int"] = df["small_int"].astype("int16")
```

For large data:

- Read only needed columns.
- Use Parquet.
- Process chunks.
- Push filtering into SQL.
- Consider Polars, Dask, DuckDB, Spark.

## 12. SQL For Data Analysis

Basic aggregation:

```sql
SELECT
    user_id,
    COUNT(*) AS orders,
    SUM(amount) AS revenue
FROM orders
GROUP BY user_id
ORDER BY revenue DESC;
```

Window function:

```sql
SELECT
    order_id,
    user_id,
    amount,
    SUM(amount) OVER (
        PARTITION BY user_id
        ORDER BY created_at
    ) AS running_total
FROM orders;
```

Common Table Expression:

```sql
WITH user_revenue AS (
    SELECT user_id, SUM(amount) AS revenue
    FROM orders
    GROUP BY user_id
)
SELECT *
FROM user_revenue
WHERE revenue > 1000;
```

## 13. Visualization Storytelling

A chart should answer a question.

Bad question:

- "Show the data."

Better question:

- "Did conversion improve after the redesign?"

Chart choices:

- Line chart: change over time.
- Bar chart: compare categories.
- Scatter plot: relationship between variables.
- Histogram: distribution.
- Box plot: spread and outliers.
- Heatmap: matrix patterns.

Example:

```python
import matplotlib.pyplot as plt

daily_revenue.plot(kind="line", title="Daily Revenue")
plt.xlabel("Date")
plt.ylabel("Revenue")
plt.tight_layout()
plt.show()
```

Story structure:

1. Context.
2. Question.
3. Evidence.
4. Uncertainty.
5. Recommendation.

## 14. Probability Basics

Probability measures uncertainty.

Rules:

```txt
0 <= P(A) <= 1
P(not A) = 1 - P(A)
P(A and B) = P(A) * P(B) if independent
P(A or B) = P(A) + P(B) - P(A and B)
```

Conditional probability:

```txt
P(A | B) = P(A and B) / P(B)
```

## 15. Random Variables

A random variable maps outcomes to numbers.

Examples:

- Number of clicks.
- Revenue per user.
- Whether user converts.
- Time until churn.

Distributions:

- Bernoulli: yes/no event.
- Binomial: number of successes in trials.
- Normal: bell-shaped continuous values.
- Poisson: counts over time/space.
- Exponential: waiting time.

## 16. Statistical Inference

Inference uses sample data to reason about a population.

Population:

- All users you care about.

Sample:

- Users you observed.

Estimator:

- Formula from sample data.

Estimate:

- Value computed from sample.

Confidence interval:

- Range of plausible values for a parameter under repeated sampling logic.

## 17. Hypothesis Testing

Basic structure:

- Null hypothesis: no effect or no difference.
- Alternative hypothesis: effect or difference exists.
- Test statistic: measured evidence.
- p-value: probability of data at least this extreme if null were true.
- Significance level: threshold like 0.05.

Important: p-value is not the probability the null is true.

## 18. t-test Example

```python
from scipy import stats

group_a = [10, 12, 9, 11, 10]
group_b = [13, 15, 12, 14, 16]

result = stats.ttest_ind(group_a, group_b, equal_var=False)
print(result.statistic, result.pvalue)
```

Use Welch's t-test when variances may differ.

## 19. A/B Testing

A/B test compares variants.

```mermaid
flowchart LR
  U["Eligible users"] --> R["Random assignment"]
  R --> A["Control"]
  R --> B["Treatment"]
  A --> M["Measure metric"]
  B --> M
  M --> D["Decision"]
```

Key requirements:

- Randomization.
- Stable metric.
- Enough sample size.
- No peeking without correction.
- Clear success criteria.
- Guardrail metrics.

## 20. Conversion Test

Two-proportion z-test idea:

```python
from statsmodels.stats.proportion import proportions_ztest

conversions = [120, 150]
visitors = [3000, 3100]

stat, p_value = proportions_ztest(conversions, visitors)
print(stat, p_value)
```

Also calculate effect size:

```python
rate_a = conversions[0] / visitors[0]
rate_b = conversions[1] / visitors[1]
lift = (rate_b - rate_a) / rate_a
```

Do not only ask "is it significant?" Ask "is it meaningful?"

## 21. Experiment Pitfalls

- Sample ratio mismatch.
- Novelty effects.
- Seasonality.
- Multiple testing.
- Stopping early.
- Metric gaming.
- User interference.
- Logging bugs.
- Segment imbalance.

## 22. Data Project Template

```python
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    clean["created_at"] = pd.to_datetime(clean["created_at"])
    clean = clean.dropna(subset=["amount"])
    return clean

def summarize_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("user_id", as_index=False)
        .agg(revenue=("amount", "sum"), orders=("order_id", "count"))
    )
```

Keep loading, cleaning, analysis, and presentation separate.

