"""Unit tests for priority score computation."""
import pytest
from src.pretransplant_pgx.priority_score import compute_priorities, PriorityEntry, ORGAN_GENE_MAP


SAMPLE_ACTIONABILITY = [
    {"gene_symbol": "CYP3A5", "population_code": "PEL", "drug_name": "tacrolimus",
     "delta_vs_baseline": -50.35, "population_affected_pct": 91.76, "classification_strength": "Strong",
     "clinical_implication": "test"},
    {"gene_symbol": "TPMT", "population_code": "MXL", "drug_name": "azathioprine",
     "delta_vs_baseline": 2.1, "population_affected_pct": 100.0, "classification_strength": "Strong",
     "clinical_implication": "test"},
    {"gene_symbol": "CYP3A5", "population_code": "CEU", "drug_name": "tacrolimus",
     "delta_vs_baseline": 0.0, "population_affected_pct": 9.09, "classification_strength": "Strong",
     "clinical_implication": "baseline"},
]

SAMPLE_WAITLIST = [
    {"country_iso3": "USA", "year": 2024, "organ": "kidney", "patients": 89000, "source": "OPTN"},
    {"country_iso3": "MEX", "year": 2024, "organ": "kidney", "patients": 8000, "source": "CENATRA"},
    {"country_iso3": "DEU", "year": 2024, "organ": "heart", "patients": 600, "source": "Eurotransplant"},
]


def test_ceu_excluded():
    results = compute_priorities(SAMPLE_ACTIONABILITY, SAMPLE_WAITLIST)
    pops = {e.population_code for e in results}
    assert "CEU" not in pops


def test_priority_score_positive():
    results = compute_priorities(SAMPLE_ACTIONABILITY, SAMPLE_WAITLIST)
    assert all(e.priority_score >= 0 for e in results)


def test_all_organs_covered():
    results = compute_priorities(SAMPLE_ACTIONABILITY, SAMPLE_WAITLIST)
    organs = {e.organ for e in results}
    assert organs <= set(ORGAN_GENE_MAP.keys())


def test_sorted_descending():
    results = compute_priorities(SAMPLE_ACTIONABILITY, SAMPLE_WAITLIST)
    scores = [e.priority_score for e in results]
    assert scores == sorted(scores, reverse=True)


def test_priority_entry_formula():
    """PriorityEntry score matches expected formula output."""
    import math
    entry = PriorityEntry(
        gene_symbol="CYP3A5",
        population_code="PEL",
        organ="kidney",
        population_affected_pct=91.76,
        delta_vs_baseline=-50.35,
        waitlist_patients=97000,
    )
    pgx = (91.76 / 100) * abs(-50.35)
    waitlist = math.log1p(97000 / 1000)
    expected = round(pgx * waitlist, 4)
    assert entry.priority_score == expected


def test_zero_waitlist_gives_zero_score():
    entry = PriorityEntry(
        gene_symbol="TPMT",
        population_code="MXL",
        organ="liver",
        population_affected_pct=100.0,
        delta_vs_baseline=2.1,
        waitlist_patients=0,
    )
    assert entry.priority_score == 0.0
