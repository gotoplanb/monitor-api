.PHONY: setup test run clean lint format ci coverage

# Python virtual environment
VENV = monitor
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Project settings
PORT = 8000
APP = app.main:app

setup:
	pipx run virtualenv $(VENV)
	. ./$(VENV)/bin/activate && \
	$(PIP) install -r requirements.txt && \
	$(PIP) install -e .

format: setup
	$(PYTHON) -m black .

lint: setup
	$(PYTHON) -m pylint $$(git ls-files '*.py')

test: setup
	TESTING=true $(PYTHON) -m pytest tests/ -v

coverage: setup
	TESTING=true $(PYTHON) -m pytest --cov=app tests/

run: setup
	$(PYTHON) -m uvicorn $(APP) --reload --port $(PORT)

ci: setup format lint test coverage

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} + 