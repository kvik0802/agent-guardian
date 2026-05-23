.PHONY: install test lint dev check-all verify demo-destroyer demo-leaker demo-undo api

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest tests/ -x -q --tb=short

verify: install test demo-destroyer demo-leaker demo-undo
	@echo "All verification passed."

lint:
	black src/ tests/ examples/
	isort src/ tests/ examples/

api:
	uvicorn agent_guardian.api.main:app --reload --port 8000

dev:
	docker-compose up -d redis
	uvicorn agent_guardian.api.main:app --reload --port 8000

demo-destroyer:
	python -c "from agent_guardian.demos import run_destroyer; run_destroyer()"

demo-leaker:
	python -c "from agent_guardian.demos import run_leaker; run_leaker()"

demo-undo:
	python -c "from agent_guardian.demos import run_undo; run_undo()"

check-all: lint test
	@echo "All checks passed. Ready to ship."
