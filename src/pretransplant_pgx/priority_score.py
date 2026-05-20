"""Compute pre-transplant genotyping priority score per gene × organ × population.

Priority = (population_affected_pct / 100) × |delta_vs_baseline| × log(1 + waitlist_weight / 1000)

Higher score = higher benefit from pre-emptive genotyping.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


# Genes with clinical relevance per organ type (CPIC A-level)
ORGAN_GENE_MAP: dict[str, list[str]] = {
    "kidney": ["CYP3A5", "TPMT", "NUDT15"],
    "liver":  ["CYP3A5", "TPMT", "NUDT15"],
    "heart":  ["CYP3A5", "TPMT", "NUDT15"],
}


@dataclass
class PriorityEntry:
    gene_symbol: str
    population_code: str
    organ: str
    population_affected_pct: float
    delta_vs_baseline: float
    waitlist_patients: int
    priority_score: float = field(init=False)

    def __post_init__(self) -> None:
        pgx_factor = (self.population_affected_pct / 100) * abs(self.delta_vs_baseline)
        waitlist_factor = math.log1p(self.waitlist_patients / 1000)
        self.priority_score = round(pgx_factor * waitlist_factor, 4)


def compute_priorities(
    actionability: list[dict],
    waitlist: list[dict],
) -> list[PriorityEntry]:
    """
    Args:
        actionability: rows from actionability_ranking.json
        waitlist: rows from world-waitlist.json
    Returns:
        PriorityEntry list sorted by priority_score DESC
    """
    # Aggregate waitlist by organ (most recent year per organ, sum across countries)
    organ_waitlist: dict[str, int] = {}
    latest_by_organ: dict[str, int] = {}
    for row in waitlist:
        organ = row.get("organ", "")
        year = int(row.get("year", 0))
        patients = int(row.get("patients", 0) or 0)
        if organ not in latest_by_organ or year > latest_by_organ[organ]:
            latest_by_organ[organ] = year
    for row in waitlist:
        organ = row.get("organ", "")
        year = int(row.get("year", 0))
        if year == latest_by_organ.get(organ):
            organ_waitlist[organ] = organ_waitlist.get(organ, 0) + int(row.get("patients", 0) or 0)

    entries: list[PriorityEntry] = []
    seen: set[str] = set()

    for row in actionability:
        gene = row.get("gene_symbol", "")
        pop = row.get("population_code", "")
        if pop == "CEU":
            continue

        for organ, genes in ORGAN_GENE_MAP.items():
            if gene not in genes:
                continue
            key = f"{gene}|{pop}|{organ}"
            if key in seen:
                continue
            seen.add(key)

            entries.append(PriorityEntry(
                gene_symbol=gene,
                population_code=pop,
                organ=organ,
                population_affected_pct=float(row.get("population_affected_pct", 0)),
                delta_vs_baseline=float(row.get("delta_vs_baseline", 0)),
                waitlist_patients=organ_waitlist.get(organ, 0),
            ))

    return sorted(entries, key=lambda e: e.priority_score, reverse=True)
