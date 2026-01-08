import argparse
import logging
from pathlib import Path

from aozora_data.text_to_html.converter import TextToHtmlConverter

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

INPUT_DIR = "utf-8"
OUTPUT_DIR = "utf-8_html"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Convert all UTF-8 text files to HTML files.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without actually converting files.",
    )
    return parser.parse_args()


def main() -> None:
    """Convert all UTF-8 text files in utf-8/ to HTML files in utf-8_html/.

    Skips if output file already exists and is newer than input file.
    """
    args = parse_args()
    input_dir = Path(INPUT_DIR)
    output_dir = Path(OUTPUT_DIR)

    if not input_dir.exists():
        logger.error(f"Source directory '{INPUT_DIR}' does not exist.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    # List all files in input directory
    files = list(input_dir.glob("*.utf8.txt"))
    logger.info(f"Found {len(files)} files in {INPUT_DIR}")
    if args.dry_run:
        logger.info("Running in dry-run mode. No files will be converted.")

    count_converted = 0
    count_skipped = 0
    count_error = 0

    for input_path in files:
        # Expected filename format: <book_id>.utf8.txt
        # Output filename format: <book_id>.html
        stem = input_path.name.replace(".utf8.txt", "")
        output_filename = f"{stem}.html"
        output_path = output_dir / output_filename

        if output_path.exists():
            input_mtime = input_path.stat().st_mtime
            output_mtime = output_path.stat().st_mtime
            if input_mtime <= output_mtime:
                count_skipped += 1
                continue

        if args.dry_run:
            logger.info(f"[Dry-Run] Would convert: {input_path} -> {output_path}")
            count_converted += 1
            continue

        try:
            converter = TextToHtmlConverter(str(input_path), str(output_path))
            converter.convert()

            logger.info(f"Converted: {input_path} -> {output_path}")
            count_converted += 1

        except Exception as e:
            logger.error(f"Failed to convert {input_path}: {e}")
            count_error += 1

    logger.info("Processing complete.")
    logger.info(f"Converted: {count_converted}, Skipped: {count_skipped}, Errors: {count_error}")


if __name__ == "__main__":
    main()
