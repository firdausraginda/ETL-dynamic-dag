WITH
    pool AS (
        SELECT
            DATE(last_update_date) AS partition_date,
            unique_key,
            complaint_description,
            source
        FROM `bigquery-public-data.austin_311.311_service_requests`
        ORDER BY 1 DESC
    )

SELECT *
FROM pool
LIMIT 10