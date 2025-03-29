# CLAUDE.md - Monitor API Guidelines

## Build/Lint/Test Commands

- Setup: `make setup` - Create venv and install deps
- Run: `make run` - Start FastAPI server
- Lint: `make lint` - Run pylint
- Format: `make format` - Run black
- Test: `make test` - Run all tests
- Single test: `python -m pytest tests/test_file.py::test_name -v`

## Code Style Guidelines

- Use Black for formatting, Pylint for linting
- Type annotations for function parameters and returns
- Classes: PascalCase, functions/variables: snake_case, constants: UPPERCASE
- Import order: stdlib, third-party, local

## Commit Guidelines

- ALWAYS run `make format` then `make lint` before committing
- Fix any formatting or linting issues before pushing
- Write clear, descriptive commit messages
- Keep commits focused and atomic

## Error Handling

- Return appropriate HTTP status codes with error messages
- Use proper exception handling with FastAPI's HTTPException

## Project Structure

- `/app` - Main application code
  - `/api` - API routes and dependencies
  - `/core` - Core functionality and config
  - `/models` - SQLAlchemy models
  - `/schemas` - Pydantic schemas

## Testing Guidelines

- Test each endpoint for success and failure cases
- Use pytest fixtures for database setup/teardown
- Mock external services when necessary
- Follow AAA pattern (Arrange, Act, Assert)