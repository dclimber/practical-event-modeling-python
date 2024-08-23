.PHONY: setup test

setup:
	poetry install

test:
	PYTHONPATH=components/ poetry run pytest tests/
