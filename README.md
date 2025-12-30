# py-aozora-data

**Aozora Bunko Data Pipeline to Firestore**

This project provides a data pipeline to download the official [Aozora Bunko](https://www.aozora.gr.jp/) book list (CSV) and import it into Google Cloud Firestore. It supports efficient differential updates by comparing existing metadata.

> [!IMPORTANT]
> This repository has been refactored. Support for SQL (SQLAlchemy) and Pydantic models has been removed in favor of direct Firestore integration.

## Features

- **Automated Import**: Downloads `list_person_all_extended_utf8.zip` from Aozora Bunko.
- **Firestore Integration**: Writes Books, Persons, and Contributors to Firestore collections (`books`, `persons`, `contributors`).
- **Differential Updates**: Minimizes writes by comparing `last_modified` dates and content hashes with existing Firestore documents.
- **Batch Processing**: Uses Firestore batch writes for performance.

## Prerequisites

- Python 3.13 or higher
- Google Cloud Project with Firestore enabled
- Google Application Default Credentials (ADC) configured

## Installation

This project uses `uv` for dependency management.

```bash
# Clone the repository
git clone https://github.com/ksato9700/py-aozora-data.git
cd py-aozora-data

# Install dependencies
uv sync
```

## Usage

### Running the Importer

Set your Google Cloud Project ID and run the importer module.

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id

# Run the importer
uv run python -m aozora_data.importer.main
```

### Configuration

You can configure the importer behavior using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | Google Cloud Project ID (Required) | - |
| `AOZORA_CSV_URL` | URL to the Aozora Bunko CSV zip file | `https://www.aozora.gr.jp/index_pages/list_person_all_extended_utf8.zip` |

## Development

```bash
# Install development dependencies
uv sync --extra dev

# Run tests
uv run pytest
```

## License

MIT
