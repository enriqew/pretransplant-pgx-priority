{{ config(materialized='view') }}

WITH raw AS (
    SELECT *
    FROM read_json_auto('{{ env_var("PGX_ACTIONABILITY_PATH", "../../data/raw/pgx_artifacts_*/actionability_ranking.json") }}')
)
SELECT
    CAST(gene_symbol AS VARCHAR)             AS gene_symbol,
    CAST(population_code AS VARCHAR)         AS population_code,
    CAST(drug_name AS VARCHAR)               AS drug_name,
    CAST(delta_vs_baseline AS DOUBLE)        AS delta_vs_baseline,
    CAST(population_affected_pct AS DOUBLE)  AS population_affected_pct,
    CAST(classification_strength AS VARCHAR) AS classification_strength,
    CAST(clinical_implication AS VARCHAR)    AS clinical_implication
FROM raw
WHERE gene_symbol IS NOT NULL
  AND population_code IS NOT NULL
