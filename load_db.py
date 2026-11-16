"""Load CSVs from data/ into a SQLite database (airbnb.db), cleaning price/boolean columns."""
import sqlite3, pandas as pd
from pathlib import Path

DATA, DB = Path("data"), Path("airbnb.db")
DB.unlink(missing_ok=True)
con = sqlite3.connect(DB)

def money(s):  # "$1,234.00" -> 1234.0
    return pd.to_numeric(s.astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce")

L = pd.read_csv(DATA / "listings.csv")
L["price"] = money(L["price"])
L = L[L.price.between(10, 5000)]                      # drop missing / absurd prices
L["host_is_superhost"] = (L.host_is_superhost == "t").astype(int)
L[["id", "name", "host_id", "host_name", "host_is_superhost", "neighbourhood_cleansed", "room_type",
   "accommodates", "bedrooms", "price", "minimum_nights", "number_of_reviews", "review_scores_rating"]
  ].to_sql("listings", con, index=False)

pd.read_csv(DATA / "reviews.csv", usecols=["listing_id", "date"]).to_sql("reviews", con, index=False)

C = pd.read_csv(DATA / "calendar.csv", usecols=["listing_id", "date", "available", "price"])
C["price"] = money(C["price"])
C["available"] = (C.available == "t").astype(int)
C.to_sql("calendar", con, index=False)

con.executescript("""
CREATE INDEX ix_cal ON calendar(listing_id);
CREATE INDEX ix_rev ON reviews(listing_id);
CREATE INDEX ix_lst_host ON listings(host_id);
""")
for t in ("listings", "reviews", "calendar"):
    print(t, con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0], "rows")
