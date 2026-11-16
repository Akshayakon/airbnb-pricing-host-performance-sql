-- Price percentiles (P10/P50/P90) by room type, using window functions (SQLite has no PERCENTILE_CONT)
WITH ranked AS (
  SELECT room_type, price,
         ROW_NUMBER() OVER (PARTITION BY room_type ORDER BY price) AS rn,
         COUNT(*)     OVER (PARTITION BY room_type)               AS n
  FROM listings
)
SELECT room_type,
       MAX(n) AS listings,
       MIN(CASE WHEN rn >= 0.10 * n THEN price END) AS p10,
       MIN(CASE WHEN rn >= 0.50 * n THEN price END) AS median,
       MIN(CASE WHEN rn >= 0.90 * n THEN price END) AS p90
FROM ranked
GROUP BY room_type
ORDER BY median DESC;
