.PHONY: install test lint dev check-all verify quickstart api

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest tests/ -x -q --tb=short

verify: install test quickstart
	@echo "All verification passed."

lint:
	black src/ tests/ examples/
	isort src/ tests/ examples/

api:
	uvicorn agent_guardian.api.main:app --reload --port 8000

dev:
	docker-compose up -d redis
	uvicorn agent_guardian.api.main:app --reload --port 8000

quickstart:
	python -c "from agent_guardian.demos import run_quickstart; run_quickstart()"

check-all: lint test
	@echo "All checks passed. Ready to ship."
