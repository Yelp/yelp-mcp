.PHONY: install build run clean help

install: check-uv
	uv sync

check-uv:
	@command -v uv >/dev/null 2>&1 || { echo >&2 "Error: 'uv' is not installed. Please install it from https://docs.astral.sh/uv/ or brew install uv"; exit 1; }

build: check-uv
	@echo "No build step required for pure Python project."

run: check-uv install
	uv run mcp-yelp-agent

clean:
	rm -rf src/yelp_agent/__pycache__
	rm -rf src/yelp_agent.egg-info
	rm -rf .venv
	rm -rf dist
	rm -rf build

help:
	@echo "Available targets:"
	@echo "  install      - Install dependencies using uv"
	@echo "  build        - Build the project (no-op for pure Python)"
	@echo "  run          - Run the main application"
	@echo "  clean        - Remove caches and virtual environment"
	@echo "  help         - Show this help message"
