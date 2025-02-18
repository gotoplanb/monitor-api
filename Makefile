.PHONY: setup test run clean lint format

# Python virtual environment
VENV = monitors
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Project settings
PORT = 8000
APP = app.main:app

setup: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	python -m venv $(VENV)
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

test: setup
	$(PYTHON) -m pytest tests/ -v

lint: setup
	$(PYTHON) -m pylint $$(git ls-files '*.py')

format: setup
	$(PYTHON) -m black .

run: setup
	$(PYTHON) -m uvicorn $(APP) --reload --port $(PORT)

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