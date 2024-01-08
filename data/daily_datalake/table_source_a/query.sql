SELECT
    DATE(last_update_date) AS partition_date,
    'a' AS col_str,
    3 AS col_int
FROM `bigquery-public-data.austin_311.311_service_requests`
LIMIT 10