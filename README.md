# EDGAR 10-K Pipeline

## Installation

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (manages Python, the virtual environment and dependencies)

### Setup

1. Install Python 3.14.6 with uv:

   ```bash
   uv python install 3.14.6
   ```

2. From the project root, create the virtual environment and install dependencies:

   ```bash
   uv sync
   ```

3. Run the application:

   ```bash
   uv run main.py
   ```

## Development

### Linting and formatting

[Ruff](https://docs.astral.sh/ruff/) is used for both linting and formatting. Its settings live in `pyproject.toml`.

Lint the code and auto-fix what can be fixed:

```bash
uv run ruff check --fix .
```

Format the code:

```bash
uv run ruff format .
```

To check without changing files (e.g. in CI):

```bash
uv run ruff check .
uv run ruff format --check .
```

### Testing

Run the test suite with [pytest](https://docs.pytest.org/):

```bash
uv run pytest
```
