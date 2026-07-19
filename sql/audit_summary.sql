-- Source-risk and normalization summary; run with sqlite3 work/migration.db.
SELECT
  COUNT(*) AS total_files,
  SUM(size_bytes) AS total_bytes,
  SUM(CASE WHEN path_length > 400 THEN 1 ELSE 0 END) AS paths_over_400,
  MAX(path_length) AS maximum_path_length,
  ROUND(AVG(directory_depth), 2) AS average_directory_depth
FROM source_inventory;

SELECT validation_status, COUNT(*) AS records
FROM normalized_documents
GROUP BY validation_status
ORDER BY validation_status;

