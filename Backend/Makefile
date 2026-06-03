.PHONY: all run-api run-api-system run-api-fallback run-ui test ci lint docker-up docker-down clean install install-ml seed

all: install lint test

run-api:
	uvicorn app.main:app --reload --port 8000

run-api-system:
	VOXPILOT_ENGINE=system uvicorn app.main:app --reload --port 8000

run-api-fallback:
	VOXPILOT_ENGINE=fallback uvicorn app.main:app --reload --port 8000

run-ui:
	streamlit run ui/streamlit_app.py

test:
	pytest tests/ -v

ci:
	VOXPILOT_ENGINE=fake pytest tests/ -v --tb=short

lint:
	python -m compileall app ui scripts tests

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	rm -rf data/generated/* data/voxpilot.db __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

install:
	uv pip install -r requirements.txt

install-ml:
	uv pip install torch torchvision
	uv pip install -r requirements-ml.txt

seed:
	python scripts/demo_seed.py
