.PHONY: install ingest transform digest all test lint fmt clean

install:
	pip install -e ".[dev]"

ingest:
	python -c "from tech_brief.pipeline import ingest_all; print(ingest_all(), 'stories ingested')"

transform:
	dbt build --project-dir dbt --profiles-dir dbt

digest:
	python -m tech_brief

all: ingest transform digest

test:
	pytest -q

lint:
	ruff check .

fmt:
	ruff format .

clean:
	rm -f data/tech_brief.duckdb data/tech_brief.duckdb.wal
	rm -rf dbt/target dbt/dbt_packages dbt/logs
