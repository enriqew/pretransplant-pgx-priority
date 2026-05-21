# Pre-Transplant Genotyping Priority

Decision-support matrix that ranks which pharmacogenes should be tested before transplantation.
Combines CPIC clinical actionability scores, LATAM allele frequency divergences, and organ-specific
waitlist volumes to identify where pre-emptive genotyping has the highest marginal benefit.

---
## What this project does

Pre-emptive pharmacogenomic testing before transplantation lets clinical teams adjust immunosuppressant
regimens at Day 1, rather than retrospectively after adverse events. The window of opportunity is the
waitlist period — months to years for kidney, shorter for heart.

This project answers: **which gene should we test first, for which organ, and for which population?**

---

## Priority Score Methodology

```
priority_score = (population_affected_pct / 100)
               × |delta_vs_baseline|
               × log(1 + waitlist_size / 1000)
```

| Component | Source | Meaning |
|---|---|---|
| `population_affected_pct` | PGx Latam Atlas (CPIC × 1000G) | % of cohort requiring dose/therapy change |
| `delta_vs_baseline` | PGx Latam Atlas | Deviation from European (CEU) baseline in pp |
| `waitlist_size` | Transplant Waitlist Atlas | Total patients waiting for that organ (most recent year, all covered countries) |

The log-scale waitlist factor prevents the USA kidney list (~95,000 patients) from eclipsing smaller but
clinically significant organ queues.

---

## Input Data

| Dataset | Location | Fields used |
|---|---|---|
| `actionability_ranking.json` | `pgx-latam-atlas` pipeline | `gene_symbol`, `drug_name`, `population_code`, `population_affected_pct`, `delta_vs_baseline`, `clinical_implication` |
| `drug_impact_summary.json` | `pgx-latam-atlas` pipeline | `gene_symbol`, `drug_name`, `population_code`, `percentage_requiring_change`, `delta_vs_baseline` |
| `world-waitlist.json` | `transplant-waitlist-atlas` pipeline | `country_iso3`, `year`, `organ`, `patients`, `source` |

Both upstream datasets are produced by sibling repositories:

- [pgx-latam-atlas](https://github.com/enriqew/pgx-latam-atlas) — 1000 Genomes × CPIC pharmacogenomics pipeline
- [transplant-waitlist-atlas](https://github.com/enriqew/transplant-waitlist-atlas) — OPTN / CENATRA / Eurotransplant waitlist pipeline

---

## Planned Stack

| Layer | Technology |
|---|---|
| Data ingestion | AWS Glue (PySpark) |
| Intermediate storage | Apache Iceberg on S3 |
| Transformation | dbt + DuckDB |
| Query layer | AWS Athena |
| Serving | Static JSON artefacts → portfolio React dashboard |

---

## Genes Covered

| Gene | Drug | Organs | Rationale |
|---|---|---|---|
| CYP3A5 | Tacrolimus | Kidney, Liver, Heart | Major tacrolimus metaboliser; *3 allele frequency varies 10–92% across LATAM cohorts |
| TPMT | Azathioprine | Kidney, Liver, Heart | Poor/intermediate metabolisers at severe toxicity risk; CPIC Level A |
| NUDT15 | Azathioprine | Kidney, Liver, Heart | Asian/LATAM populations carry *3 variant at higher frequency than CEU; CPIC Level A |

---

## How to Interpret Priorities

1. **High priority score** = large fraction of the population requires dose adjustment AND the population
   diverges substantially from European dosing guidelines AND many patients are waiting for that organ.

2. **CYP3A5 dominates kidney/liver/heart** because tacrolimus is the primary immunosuppressant for all
   three organ types, and CYP3A5*3 frequency in LATAM cohorts (particularly PEL and MXL) differs
   markedly from the CEU baseline used by standard dosing guidelines.

3. **TPMT and NUDT15** are critical for azathioprine (maintenance immunosuppression post-transplant).
   Poor metabolisers are at risk of life-threatening myelosuppression at standard doses.

4. **Waitlist factor** scales the score by the logarithm of the waitlist size, giving larger programmes
   more weight without allowing them to completely dominate the ranking.

---

## Limitations

- **Proxy populations.** 1000 Genomes LATAM cohorts (MXL, PEL, CLM, PUR) are not direct
  clinical populations — they are research cohorts with specific recruitment criteria.

- **Diplotype assumptions.** Phenotype assignment follows CPIC star-allele → phenotype mapping.
  Novel or rare variants not captured in 1000G phase 3 are excluded.

- **Waitlist data coverage.** World-waitlist data covers USA (OPTN), México (CENATRA), and
  Eurotransplant member states. Large waitlists in Brazil, Argentina, and Colombia are not yet included,
  which understates LATAM-specific demand.

- **Single priority metric.** The composite score combines three signals into one number for
  decision support. It does not replace clinical pharmacogenomics consultation or institutional
  protocols.

- **No graft-specific pharmacokinetics.** The score does not model organ-specific drug metabolism
  differences (e.g., liver transplant recipients have different CYP3A5 expression post-surgery).

---

## Live Dashboard

The interactive priority matrix is embedded in the portfolio at
[enriqueredonda.dev/projects/pretransplant-pgx-priority](https://db0dj7zz9je7r.cloudfront.net/projects/pretransplant-pgx-priority).

---

## License

MIT
