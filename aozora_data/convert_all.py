import logging
from pathlib import Path

from aozora_data.sjis_to_utf8.converter import convert_content

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SJIS_DIR = "sjis"
OUTPUT_DIR = "utf-8"


def main() -> None:
    """Convert all SJIS files in sjis/ to UTF-8 files in utf-8/.

    Skips if output file already exists.
    """
    sjis_dir = Path(SJIS_DIR)
    output_dir = Path(OUTPUT_DIR)

    if not sjis_dir.exists():
        logger.error(f"Source directory '{SJIS_DIR}' does not exist.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    # List all files in sjis directory
    files = list(sjis_dir.glob("*.sjis.txt"))
    logger.info(f"Found {len(files)} files in {SJIS_DIR}")

    count_converted = 0
    count_skipped = 0
    count_error = 0

    for sjis_path in files:
        # Expected filename format: <book_id>.sjis.txt
        # Output filename format: <book_id>.utf8.txt
        stem = sjis_path.name.replace(".sjis.txt", "")
        output_filename = f"{stem}.utf8.txt"
        output_path = output_dir / output_filename

        if output_path.exists():
            count_skipped += 1
            continue

        try:
            with open(sjis_path, "rb") as f:
                content_sjis = f.read()

            utf8_text = convert_content(content_sjis)
            utf8_bytes = utf8_text.encode("utf-8")

            with open(output_path, "wb") as f:
                f.write(utf8_bytes)

            logger.info(f"Converted: {sjis_path} -> {output_path}")
            count_converted += 1

        except Exception as e:
            logger.error(f"Failed to convert {sjis_path}: {e}")
            count_error += 1

    logger.info("Processing complete.")
    logger.info(f"Converted: {count_converted}, Skipped: {count_skipped}, Errors: {count_error}")


if __name__ == "__main__":
    main()
