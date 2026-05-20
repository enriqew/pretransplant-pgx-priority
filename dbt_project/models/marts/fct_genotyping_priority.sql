{{ config(materialized='table') }}

WITH organ_waitlist AS (
    SELECT
        organ,
        MAX(year) AS latest_year,
        SUM(patients) AS total_patients
    FROM {{ ref('stg_waitlist_stock') }}
    GROUP BY organ
),
pgx_ranked AS (
    SELECT
        a.gene_symbol,
        a.population_code,
        a.drug_name,
        a.delta_vs_baseline,
        a.population_affected_pct,
        a.classification_strength,
        a.clinical_implication,
        ROW_NUMBER() OVER (
            PARTITION BY a.gene_symbol, a.population_code
            ORDER BY ABS(a.delta_vs_baseline) DESC
        ) AS rn
    FROM {{ ref('stg_pgx_actionability') }} a
    WHERE a.population_code != 'CEU'
),
deduped AS (
    SELECT * FROM pgx_ranked WHERE rn = 1
),
organ_gene_map AS (
    SELECT * FROM (VALUES
        ('kidney', 'CYP3A5'), ('kidney', 'TPMT'), ('kidney', 'NUDT15'),
        ('liver',  'CYP3A5'), ('liver',  'TPMT'), ('liver',  'NUDT15'),
        ('heart',  'CYP3A5'), ('heart',  'TPMT'), ('heart',  'NUDT15')
    ) AS t(organ, gene_symbol)
)
SELECT
    d.gene_symbol,
    d.population_code,
    m.organ,
    d.drug_name,
    d.population_affected_pct,
    d.delta_vs_baseline,
    d.classification_strength,
    d.clinical_implication,
    COALESCE(w.total_patients, 0) AS waitlist_patients,
    ROUND(
        (d.population_affected_pct / 100.0) * ABS(d.delta_vs_baseline) * LN(1 + COALESCE(w.total_patients, 0) / 1000.0),
        4
    ) AS priority_score
FROM deduped d
JOIN organ_gene_map m ON d.gene_symbol = m.gene_symbol
LEFT JOIN organ_waitlist w ON m.organ = w.organ
ORDER BY priority_score DESC
