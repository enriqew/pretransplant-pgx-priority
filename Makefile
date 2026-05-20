.PHONY: install ingest-pgx ingest-waitlist transform test lint clean

install:
	pip install -e ".[dev]"

# ── Ingest ────────────────────────────────────────────────────────────────────
ingest-pgx:
	python -m ingest.pgx_artifacts

ingest-waitlist:
	python -m ingest.waitlist_artifacts

ingest: ingest-pgx ingest-waitlist

# ── dbt ──────────────────────────────────────────────────────────────────────
transform:
	cd dbt_project && dbt run --profiles-dir .

dbt-test:
	cd dbt_project && dbt test --profiles-dir .

# ── Priority export ───────────────────────────────────────────────────────────
export:
	python -c "from src.pretransplant_pgx.export import run; run()"

# ── Tests & lint ──────────────────────────────────────────────────────────────
test:
	pytest tests/ -v --tb=short

lint:
	ruff check src/ ingest/ tests/

# ── Cleanup ──────────────────────────────────────────────────────────────────
clean:
	find data/raw -mindepth 1 -not -name '.gitkeep' -delete 2>/dev/null || true
	find artifacts -mindepth 1 -not -name '.gitkeep' -delete 2>/dev/null || true
