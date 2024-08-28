.PHONY: setup test

setup:
	poetry install

test:
	PYTHONPATH=src/ poetry run pytest tests/
