"""Create a synthetic dataset using the Inside Airbnb schema (subset of columns).
Skip this script if you drop real Inside Airbnb listings.csv / reviews.csv / calendar.csv into data/."""
import numpy as np, pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
out = Path("data"); out.mkdir(exist_ok=True)

N_LISTINGS, N_HOSTS = 1500, 200
hoods = {  # neighbourhood: price multiplier
    "Downtown": 1.5, "Waterfront": 1.4, "Old Town": 1.2, "Midtown": 1.1,
    "University District": 0.95, "Eastside": 0.85, "Northside": 0.8, "Airport Area": 0.65,
}
room_mult = {"Entire home/apt": 1.0, "Private room": 0.45, "Shared room": 0.25}

host_ids = np.arange(1000, 1000 + N_HOSTS)
host_weights = rng.pareto(1.5, N_HOSTS) + 1          # a few hosts own many listings
host_weights /= host_weights.sum()
host_super = dict(zip(host_ids, rng.random(N_HOSTS) < 0.3))

rows = []
for i in range(N_LISTINGS):
    lid = 50000 + i
    h = rng.choice(host_ids, p=host_weights)
    hood = rng.choice(list(hoods), p=[.16, .1, .12, .15, .12, .13, .12, .10])
    room = rng.choice(list(room_mult), p=[.65, .31, .04])
    beds = 0 if room != "Entire home/apt" else int(rng.choice([0, 1, 2, 3, 4], p=[.1, .4, .3, .13, .07]))
    accom = max(1, int(1.8 * max(beds, 1) + rng.integers(0, 2)))
    rating = float(np.clip(rng.normal(4.7, 0.25), 3.0, 5.0))
    price = 90 * hoods[hood] * room_mult[room] * (1 + 0.45 * beds) * (1 + 0.08 * (rating - 4.7) * 5)
    price *= 1.1 if host_super[h] else 1.0
    price = round(price * rng.lognormal(0, 0.18), 0)
    rows.append(dict(id=lid, name=f"Listing {lid}", host_id=h, host_name=f"Host_{h}",
                     host_is_superhost="t" if host_super[h] else "f",
                     neighbourhood_cleansed=hood, room_type=room, accommodates=accom,
                     bedrooms=beds if room == "Entire home/apt" else 1,
                     price=f"${price:,.2f}", minimum_nights=int(rng.choice([1, 2, 3, 7, 30], p=[.4, .25, .15, .1, .1])),
                     number_of_reviews=0, review_scores_rating=round(rating, 2)))
listings = pd.DataFrame(rows)

# calendar: 365 days, seasonal price, availability (cheaper / superhost listings book more)
days = pd.date_range("2025-01-01", periods=365)
season = 1 + 0.2 * np.sin((days.day_of_year.values - 80) / 365 * 2 * np.pi)
weekend = np.where(days.day_of_week.values >= 4, 1.1, 1.0)
cal_parts = []
for r in listings.itertuples():
    p = float(r.price.replace("$", "").replace(",", ""))
    hood_mean = 90 * hoods[r.neighbourhood_cleansed]
    p_booked = np.clip(0.75 - 0.0012 * (p - hood_mean) + 0.06 * (r.host_is_superhost == "t")
                       + 0.1 * (r.review_scores_rating - 4.7), 0.1, 0.92)
    booked = rng.random(365) < p_booked
    cal_parts.append(pd.DataFrame({
        "listing_id": r.id, "date": days.strftime("%Y-%m-%d"),
        "available": np.where(booked, "f", "t"),
        "price": [f"${x:,.2f}" for x in p * season * weekend]}))
calendar = pd.concat(cal_parts)

# reviews: roughly proportional to booked nights
booked_n = calendar.assign(b=calendar.available.eq("f")).groupby("listing_id").b.sum()
rev = []
for lid, b in booked_n.items():
    n = rng.poisson(b / 6)
    d = pd.to_datetime("2024-01-01") + pd.to_timedelta(rng.integers(0, 365, n), unit="D")
    rev.append(pd.DataFrame({"listing_id": lid, "date": d.strftime("%Y-%m-%d"),
                             "reviewer_id": rng.integers(1_000_000, 9_000_000, n)}))
reviews = pd.concat(rev).reset_index(drop=True)
reviews.insert(0, "id", np.arange(len(reviews)))
listings["number_of_reviews"] = listings.id.map(reviews.listing_id.value_counts()).fillna(0).astype(int)

listings.to_csv(out / "listings.csv", index=False)
reviews.to_csv(out / "reviews.csv", index=False)
calendar.to_csv(out / "calendar.csv", index=False)
print(f"listings={len(listings):,} reviews={len(reviews):,} calendar={len(calendar):,}")
