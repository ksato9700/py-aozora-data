# py-aozora-data

Access library and data model for the [Aozora Bunko](https://www.aozora.gr.jp/) database.

This project provides Pydantic models for Aozora Bunko entities (Books, Persons, Workers) and tools to import the official Aozora Bunko data (CSV) into a relational database using SQLAlchemy.

## Features

- **Data Models**: Strongly typed Pydantic models for `Book`, `Person`, `Worker`, and `Contributor`.
- **Database Support**: Abstracted database access layer using SQLAlchemy.
- **Data Importer**: Utilities to download and import:
  - The comprehensive book list CSV (`list_person_all_extended_utf8.zip`).
  - Worker ID lists.

## Installation

This project requires Python 3.13 or higher.

```bash
# Clone the repository
git clone https://github.com/ksato9700/py-aozora-data.git
cd py-aozora-data

# Install dependencies
pip install .

# Or using uv (recommended for development)
uv sync
```

## Usage

### Importing Data

To populate your database with the latest Aozora Bunko data, run the importer module. This will download the latest indices from Aozora Bunko and store them in your local database.

By default, it creates an SQLite database `aozora.db` in the current directory.

```bash
python -m aozora_data.importer.main
```

### Configuration

You can configure the importer behavior using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `AOZORA_DB_URL` | Database connection URL (SQLAlchemy format) | `sqlite:///./aozora.db` |
| `AOZORA_CSV_URL` | URL to the Aozora Bunko CSV zip file | `https://www.aozora.gr.jp/index_pages/list_person_all_extended_utf8.zip` |
| `AOZORA_PID_URL` | URL to the Worker ID list | `http://reception.aozora.gr.jp/widlist.php?page=1&pagerow=-1` |

### Using as a Library

You can use the provided `DB` class to query the database using Pydantic models.

```python
from aozora_data.db.db_rdb import DB

# Initialize DB connection (point to your imported database)
db = DB("sqlite:///aozora.db")

# Fetch a book by ID
book = db.get_book(1)
if book:
    print(f"Title: {book.title}")
    print(f"Release Date: {book.release_date}")

# Query books with filters
books = db.get_books({"title": "こころ"})
for b in books:
   print(f"{b.book_id}: {b.title}")
```

## Development

This project uses `uv` for dependency management and `pytest` for testing.

```bash
# Install development dependencies
uv sync --extra dev

# Run tests
pytest
```

## License

MIT
