# Makefile for frontend development and testing

.PHONY: help install test test-auth test-forms test-api test-tables test-main test-coverage test-verbose clean lint format run dev

# Help target
help:
	@echo "Available targets:"
	@echo "  install      - Install testing dependencies"
	@echo "  test         - Run all tests"
	@echo "  test-auth    - Run authentication tests only"
	@echo "  test-forms   - Run forms tests only"
	@echo "  test-api     - Run API client tests only"
	@echo "  test-tables  - Run tables tests only"
	@echo "  test-main    - Run main app tests only"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  test-verbose - Run tests with verbose output"
	@echo "  clean        - Clean test artifacts"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code"
	@echo "  run          - Run Streamlit app"
	@echo "  dev          - Run app in development mode"

# Install testing dependencies
install:
	pip install -r ../requirements.txt

# Run all tests
test:
	pytest

# Run specific test modules
test-auth:
	pytest tests/test_components_auth.py -v

test-forms:
	pytest tests/test_components_forms.py -v

test-api:
	pytest tests/test_components_api_client.py -v

test-tables:
	pytest tests/test_components_tables.py -v

test-main:
	pytest tests/test_main.py -v

# Run tests with coverage
test-coverage:
	pytest --cov=components --cov-report=term-missing --cov-report=html

# Run tests with verbose output
test-verbose:
	pytest -v --tb=long

# Run tests by markers
test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

test-slow:
	pytest -m slow

# Clean test artifacts
clean:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	rm -rf components/__pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Code quality
lint:
	flake8 components/ tests/ main.py --max-line-length=120 --ignore=E501,W503

format:
	black components/ tests/ main.py --line-length=120

# Run application
run:
	streamlit run main.py

dev:
	streamlit run main.py --server.runOnSave true --server.address 0.0.0.0 --server.port 8501

# Testing with different Python versions (if available)
test-py39:
	python3.9 -m pytest

test-py310:
	python3.10 -m pytest

test-py311:
	python3.11 -m pytest

# Performance testing
test-performance:
	pytest -m "not slow" --durations=10

# Testing with specific configurations
test-ci:
	pytest --cov=components --cov-report=xml --junitxml=junit.xml

# Watch mode for development
test-watch:
	pytest-watch --clear --runner "pytest --tb=short"

# Generate test report
test-report:
	pytest --html=report.html --self-contained-html

# Test specific components in isolation
test-auth-only:
	pytest tests/test_components_auth.py::TestRequireAuthDecorator -v

test-forms-validation:
	pytest tests/test_components_forms.py::TestFormValidation -v

test-api-auth:
	pytest tests/test_components_api_client.py::TestFinanzasAPIAuthentication -v

# Environment setup for testing
setup-test-env:
	@echo "Setting up test environment..."
	@echo "TESTING=true" > .env.test
	@echo "DATABASE_URL=sqlite:///test.db" >> .env.test
	@echo "SECRET_KEY=test_secret_key" >> .env.test

# Debugging helpers
debug-auth:
	pytest tests/test_components_auth.py::TestRequireAuthDecorator::test_require_auth_allows_authenticated_user -v -s --pdb

debug-forms:
	pytest tests/test_components_forms.py::TestTransactionForm::test_transaction_form_successful_submission -v -s --pdb

debug-api:
	pytest tests/test_components_api_client.py::TestFinanzasAPIAuthentication::test_login_successful -v -s --pdb