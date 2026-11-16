-- Top 10 hosts by estimated revenue: joins listings, calendar and reviews.
WITH cal AS (
  SELECT listing_id,
         SUM(CASE WHEN available = 0 THEN price ELSE 0 END) AS revenue,
         1.0 * SUM(1 - available) / COUNT(*)                AS occupancy
  FROM calendar GROUP BY listing_id
), rev AS (
  SELECT listing_id, COUNT(*) AS reviews FROM reviews GROUP BY listing_id
)
SELECT l.host_id, l.host_name,
       MAX(l.host_is_superhost)             AS superhost,
       COUNT(*)                             AS listings,
       ROUND(AVG(l.price),0)                AS avg_price,
       ROUND(AVG(l.review_scores_rating),2) AS avg_rating,
       COALESCE(SUM(rev.reviews),0)         AS total_reviews,
       ROUND(100*AVG(cal.occupancy),1)      AS occupancy_pct,
       ROUND(SUM(cal.revenue),0)            AS est_annual_revenue
FROM listings l
JOIN cal ON cal.listing_id = l.id
LEFT JOIN rev ON rev.listing_id = l.id
GROUP BY l.host_id, l.host_name
ORDER BY est_annual_revenue DESC
LIMIT 10;
