-- Do bigger hosts / superhosts perform better? Segment hosts by portfolio size.
WITH host AS (
  SELECT l.host_id, COUNT(*) AS n, MAX(l.host_is_superhost) AS superhost,
         AVG(l.price) AS price, AVG(l.review_scores_rating) AS rating, AVG(o.occ) AS occ
  FROM listings l
  JOIN (SELECT listing_id, 1.0*SUM(1-available)/COUNT(*) AS occ FROM calendar GROUP BY listing_id) o
    ON o.listing_id = l.id
  GROUP BY l.host_id
)
SELECT CASE WHEN n = 1 THEN '1 listing' WHEN n <= 5 THEN '2-5 listings' ELSE '6+ listings' END AS segment,
       superhost, COUNT(*) AS hosts, ROUND(AVG(price),0) AS avg_price,
       ROUND(AVG(rating),2) AS avg_rating, ROUND(100*AVG(occ),1) AS occupancy_pct
FROM host GROUP BY segment, superhost ORDER BY segment, superhost DESC;
