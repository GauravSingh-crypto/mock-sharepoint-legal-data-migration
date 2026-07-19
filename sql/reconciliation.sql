-- Migration integrity result.
SELECT migration_status, integrity_status, COUNT(*) AS records
FROM migration_results
GROUP BY migration_status, integrity_status
ORDER BY migration_status, integrity_status;

SELECT source_path, destination_path
FROM normalized_documents
WHERE destination_path IS NOT NULL
  AND LENGTH(destination_path) > 240;

