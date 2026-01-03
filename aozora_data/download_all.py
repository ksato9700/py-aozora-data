import argparse
import csv
import io
import logging
import zipfile
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SJIS_DIR = "sjis"


def process_entry(book_id: str, url: str) -> None:
    """Download and extract SJIS content."""
    sjis_dir = Path(SJIS_DIR)
    sjis_dir.mkdir(parents=True, exist_ok=True)

    sjis_path = sjis_dir / f"{book_id}.sjis.txt"

    # Skip if already exists
    if sjis_path.exists():
        logger.info(f"Skipping (already exists): {sjis_path}")
        return

    if not url.lower().endswith(".zip"):
        logger.warning(f"Skipping non-ZIP URL: {url}")
        return

    try:
        logger.info(f"Downloading: {url} (BookID: {book_id})")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Find the first .txt file
            text_filename = None
            for name in z.namelist():
                if name.lower().endswith(".txt"):
                    text_filename = name
                    break

            if not text_filename:
                logger.error(f"No .txt file found in zip: {url}")
                return

            logger.info(f"Extracting: {text_filename}")
            with z.open(text_filename) as f:
                content_sjis = f.read()

            # Save to SJIS file
            with open(sjis_path, "wb") as f:
                f.write(content_sjis)
            logger.info(f"Saved to: {sjis_path}")

    except Exception as e:
        logger.error(f"Failed to process {url}: {e}")


def main() -> None:
    """Download Aozora Bunko text files to sjis/ directory."""
    parser = argparse.ArgumentParser(
        description="Download Aozora Bunko text files to sjis/ directory."
    )
    parser.add_argument("csv_file", help="Path to a CSV file containing 'BookID,URL'.")
    args = parser.parse_args()

    csv_file_path = Path(args.csv_file)
    if not csv_file_path.exists():
        logger.error(f"CSV file not found: {csv_file_path}")
        return

    entries = []
    with open(csv_file_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                book_id = row[0].strip()
                url = row[1].strip()
                if book_id and url and url.startswith("http"):
                    entries.append((book_id, url))
                elif book_id and url:
                    logger.warning(f"Skipping invalid row: {row}")

    logger.info(f"Found {len(entries)} entries to process.")

    for book_id, url in entries:
        process_entry(book_id, url)


if __name__ == "__main__":
    main()
