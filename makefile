.PHONY: test
test:
	uv run pytest --cov=flask_mvc --cov-report=xml --cov-report=term-missing -vvv

.PHONY: format
format:
	uv run black -l 89 tests flask_mvc

.PHONY: check
check:
	uv run black -l 89 --check flask_mvc tests
