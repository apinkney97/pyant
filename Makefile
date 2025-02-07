
test:
	uv run pytest

coverage:
	uv run pytest --cov=ant --cov-report term-missing

fmt:
	uv run toml-sort -i pyproject.toml
	uv run ruff check --fix
	uv run ruff format

typecheck:
	uv run mypy
