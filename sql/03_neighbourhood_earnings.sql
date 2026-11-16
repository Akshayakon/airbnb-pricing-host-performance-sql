-- Which neighbourhoods earn the most? Joins listings + calendar.
-- Occupancy = share of calendar days NOT available (includes host-blocked days, so it is an upper bound).
-- Est. annual revenue per listing = sum of calendar price on booked nights.
WITH listing_rev AS (
  SELECT l.id, l.neighbourhood_cleansed AS neighbourhood, l.price,
         1.0 * SUM(1 - c.available) / COUNT(*)                  AS occupancy,
         SUM(CASE WHEN c.available = 0 THEN c.price ELSE 0 END) AS annual_revenue
  FROM listings l JOIN calendar c ON c.listing_id = l.id
  GROUP BY l.id
)
SELECT neighbourhood,
       COUNT(*)                     AS listings,
       ROUND(AVG(price),0)          AS avg_nightly_price,
       ROUND(100*AVG(occupancy),1)  AS occupancy_pct,
       ROUND(AVG(annual_revenue),0) AS avg_revenue_per_listing,
       ROUND(SUM(annual_revenue),0) AS total_revenue
FROM listing_rev
GROUP BY neighbourhood
ORDER BY avg_revenue_per_listing DESC;
