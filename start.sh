#!/bin/sh
set -e

uv run alembic upgrade head
uv run fastapi run --port ${PORT:-8000}
