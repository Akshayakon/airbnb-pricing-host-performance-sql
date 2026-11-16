# Airbnb Pricing & Host Performance (SQL project)

A SQL analysis of Airbnb pricing, neighbourhood earnings and host performance, built on SQLite and the Inside Airbnb schema.

> **Note:** the bundled data is synthetic, generated to mirror the Inside Airbnb schema. The findings demonstrate the method, not real market results. Swap in real data (see below) to get real insights.

**Questions:** What drives price? Which neighbourhoods earn the most? Who are the top hosts?

## Run it
```
pip install -r requirements.txt
python generate_sample_data.py   # skip if you use real data
python load_db.py                # CSVs -> airbnb.db (SQLite)
python run_analysis.py           # runs sql/*.sql, prints + saves results/*.csv
```

## Use real Inside Airbnb data
Download `listings.csv`, `reviews.csv`, `calendar.csv` for a city from <http://insideairbnb.com/get-the-data/>
(use the detailed `listings.csv.gz`, unzipped, since the summary file lacks `bedrooms`/ratings),
put them in `data/`, then run `load_db.py` and `run_analysis.py`. The bundled generator uses the same column names.
Neighbourhood/room type values in `02_price_drivers.sql` are generic, so no query edits are needed (`bedrooms` can be NULL in real data).

> The included data is **synthetic** (Inside Airbnb blocks scripted downloads), so the findings below only demonstrate the method.

## Queries (`sql/`)
| File | Skill shown | Answers |
|---|---|---|
| 01_price_distribution | window functions, percentiles | P10/median/P90 price by room type |
| 02_price_drivers | UNION ALL, CASE bucketing | price by bedrooms, room type, superhost, rating, area |
| 03_neighbourhood_earnings | join listings + calendar, CTE | occupancy and est. revenue per neighbourhood |
| 04_top_hosts | join listings + calendar + reviews | top 10 hosts by est. revenue |
| 05_host_segments | nested aggregation | portfolio size / superhost vs. performance |

## Method notes
- **Occupancy** = share of calendar days with `available = 0`. This includes host-blocked days, so it is an upper bound.
  A review-based alternative: `reviews_per_month / 0.5 * avg_stay_nights / 30`.
- **Revenue** = sum of calendar price on unavailable days (no cleaning fees, taxes, or discounts).

## Findings (on sample data)
- **Room type and size dominate price:** entire homes median $163 vs. $43 for private rooms; each added bedroom adds roughly $45-60/night.
- **Location is next:** Downtown averages $172/night vs. $75 near the Airport.
- **Earnings follow price, not occupancy:** occupancy is ~73% everywhere, so Downtown earns about 2x Airport Area per listing ($42k vs. $20k).
- **Top hosts are portfolio owners:** the top 2 hosts (100+ listings each) out-earn the next 8 combined; superhosts run ~3-4 points higher occupancy.
