-- What drives price? Average price sliced by each candidate driver, stacked into one result.
SELECT 'bedrooms' AS driver, CAST(bedrooms AS TEXT) AS level, COUNT(*) AS listings, ROUND(AVG(price),0) AS avg_price
FROM listings WHERE room_type = 'Entire home/apt' GROUP BY bedrooms
UNION ALL
SELECT 'room_type', room_type, COUNT(*), ROUND(AVG(price),0) FROM listings GROUP BY room_type
UNION ALL
SELECT 'superhost', CASE host_is_superhost WHEN 1 THEN 'yes' ELSE 'no' END, COUNT(*), ROUND(AVG(price),0)
FROM listings GROUP BY host_is_superhost
UNION ALL
SELECT 'rating_band',
       CASE WHEN review_scores_rating >= 4.9 THEN '4.9+' WHEN review_scores_rating >= 4.7 THEN '4.7-4.89'
            WHEN review_scores_rating >= 4.4 THEN '4.4-4.69' ELSE '<4.4' END,
       COUNT(*), ROUND(AVG(price),0)
FROM listings GROUP BY 2
UNION ALL
SELECT 'neighbourhood', neighbourhood_cleansed, COUNT(*), ROUND(AVG(price),0)
FROM listings GROUP BY neighbourhood_cleansed
ORDER BY driver, avg_price DESC;
