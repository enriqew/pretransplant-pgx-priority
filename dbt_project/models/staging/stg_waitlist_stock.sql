{{ config(materialized='view') }}

WITH raw AS (
    SELECT *
    FROM read_json_auto('{{ env_var("WAITLIST_PATH", "../../data/raw/waitlist_artifacts_*/world-waitlist.json") }}')
)
SELECT
    CAST(country_iso3 AS VARCHAR) AS country_iso3,
    CAST(year AS INTEGER)         AS year,
    CAST(organ AS VARCHAR)        AS organ,
    CAST(patients AS INTEGER)     AS patients,
    CAST(source AS VARCHAR)       AS source
FROM raw
WHERE organ IS NOT NULL
  AND year IS NOT NULL
  AND patients IS NOT NULL
