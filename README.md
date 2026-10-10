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

## Running with Docker

Requires [Docker](https://docs.docker.com/get-docker/) with Docker Compose.

### Environment variables

| Variable           | Default        | Description                                                    |
| ------------------ | -------------- | -------------------------------------------------------------- |
| `COMPANIES`        | _default list_ | Comma-separated company names or tickers to fetch the 10-K for |
| `INTERVAL_SECONDS` | `3600`         | Seconds to wait between pipeline cycles                        |
| `LOG_LEVEL`        | `INFO`         | Log verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`)            |

All variables are optional. If `COMPANIES` is missing or empty, the pipeline uses the default list:

```text
Apple,Meta,Alphabet,Amazon,Netflix,Goldman Sachs
```

Company names are matched case-insensitively against the SEC ticker list, either as a substring of the company title (e.g. `Meta Platforms`) or as an exact ticker (e.g. `NVDA`).

Set them in a `.env` file in the project root (picked up automatically by Docker Compose):

```dotenv
COMPANIES=Apple,Microsoft,NVDA,Meta Platforms
INTERVAL_SECONDS=1800
LOG_LEVEL=INFO
```

Or pass them inline:

```bash
COMPANIES="Apple,Tesla" INTERVAL_SECONDS=600 docker compose up --build
```

### Usage

Build and start the pipeline in the background:

```bash
docker compose up -d --build
```

Follow the logs:

```bash
docker compose logs -f
```

Sample output:

```text
INFO edgar-10k-pipeline: Cycle 1 started
INFO edgar-10k-pipeline: [Apple] Resolved to Apple Inc. (AAPL, CIK 320193)
INFO edgar-10k-pipeline: [Apple] Fetching most recent 10-K
INFO edgar-10k-pipeline: [Apple] PDF generated: pdfs/Apple Inc._AAPL_320193.pdf (439681 bytes)
WARNING edgar-10k-pipeline: [Nonexistent Corp] Company not found in SEC ticker list
INFO edgar-10k-pipeline: Cycle 1 finished, sleeping 3600s
```

Stop the pipeline:

```bash
docker compose down
```

The container mounts two directories from the project root:

- `.cache/` — HTTP responses and rendered PDFs, reused across restarts
- `pdfs/` — generated 10-K PDFs, named `{title}_{ticker}_{cik}.pdf`

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
