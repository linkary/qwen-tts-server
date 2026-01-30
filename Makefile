.PHONY: help install run docker-build docker-up docker-down clean test

help:
	@echo "Qwen3-TTS API Server - Available commands:"
	@echo "  make install      - Install dependencies locally"
	@echo "  make run          - Run server locally"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start with Docker Compose"
	@echo "  make docker-down  - Stop Docker Compose"
	@echo "  make test         - Run API tests"
	@echo "  make clean        - Clean generated files"

install:
	pip install -r requirements.txt

run:
	python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
	@echo "Server started! Access at http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

test:
	python test_api.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.wav" -delete
	rm -rf output/*.wav
