SHELL := /bin/bash

.PHONY: all clean test install run deploy down deploy-react deploy-api

all: clean test install run deploy down

test:
	poetry run pytest tests -vv --show-capture=all

install: generate_dot_env
	pip install --upgrade pip
	pip install poetry
	poetry install --with dev

run:
	echo 'load your google key.json file to key.json or adjust the path'
	export GOOGLE_APPLICATION_CREDENTIALS=key.json
	PYTHONPATH=lifex_users_api/ poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8089 --log-level trace

deploy-api:
	bash scripts/deploy_cloud_run.sh deploy
deploy-react:
	bash scripts/deploy_cloud_run.sh deployVocodeDemo
deploy:
	bash scripts/deploy_cloud_run.sh deploy
	bash scripts/deploy_cloud_run.sh deployVocodeDemo

destroy:
	gcloud run services delete lifex-backend-api-v1

down:
	docker-compose down

generate_dot_env:
	@if [[ ! -e .env ]]; then \
		cp .env.example .env; \
	fi

clean:
	@find . -name '*.pyc' -exec rm -rf {} \;
	@find . -name '__pycache__' -exec rm -rf {} \;
	@find . -name 'Thumbs.db' -exec rm -rf {} \;
	@find . -name '*~' -exec rm -rf {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf docs/_build