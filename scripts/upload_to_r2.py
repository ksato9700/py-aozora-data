import csv
import hashlib
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
SOURCE_DIR = "utf-8"
MAX_WORKERS = 10  # Number of parallel uploads


def get_r2_client():
    """Create and return a boto3 client for Cloudflare R2."""
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME]):
        logger.error("Missing required environment variables.")
        logger.error(
            "Please set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, and R2_BUCKET_NAME."
        )
        raise ValueError("Missing environment variables")

    return boto3.client(
        "s3",
        endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


def calculate_md5(file_path: Path) -> str:
    """Calculate the MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def upload_file(client: object, file_path: Path, bucket_name: str, dry_run: bool = False):
    """Upload a single file to R2."""
    try:
        # Calculate local MD5
        local_md5 = calculate_md5(file_path)

        # Check if file exists and matches MD5
        try:
            # client is explicitly typed as object to avoid ANN401, but at runtime it's a boto3 client
            response = client.head_object(Bucket=bucket_name, Key=file_path.name)  # type: ignore
            remote_etag = response.get("ETag", "").strip('"')

            if local_md5 == remote_etag:
                if dry_run:
                    logger.info(f"[DRY RUN] Would skip {file_path.name} (unchanged)")
                else:
                    logger.info(f"Skipped: {file_path.name} (unchanged)")
                return True
        except ClientError as e:
            # If 404, object doesn't exist, proceed to upload
            error_code = e.response.get("Error", {}).get("Code")
            if error_code != "404" and error_code != "NotFound":
                logger.warning(f"Could not check existence of {file_path.name}: {e}")
                # Proceed to upload if unrelated error

        if dry_run:
            logger.info(f"[DRY RUN] Would upload {file_path.name} to {bucket_name}")
            return True

        extra_args = {
            "ContentType": "text/plain; charset=utf-8"  # Force text/plain for .txt files
        }

        with open(file_path, "rb") as f:
            # client is explicitly typed as object to avoid ANN401
            client.upload_fileobj(f, bucket_name, file_path.name, ExtraArgs=extra_args)  # type: ignore
        logger.info(f"Uploaded: {file_path.name}")
        return True
    except ClientError as e:
        logger.error(f"Failed to upload {file_path.name}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error processing {file_path.name}: {e}")
        return False


def load_allowed_work_ids(csv_path: Path) -> set[str]:
    """Load work IDs that have no copyright (flag is 'なし')."""
    allowed_ids = set()
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return set()

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            next(reader)  # Skip header
        except StopIteration:
            return set()

        for row in reader:
            if len(row) <= 10:
                continue

            work_id = row[0]
            copyright_flag = row[10]

            if copyright_flag == "なし":
                allowed_ids.add(work_id)

    logger.info(f"Loaded {len(allowed_ids)} copyright-free work IDs")
    return allowed_ids


def get_filtered_files(source_dir: Path, allowed_ids: set[str]) -> list[Path]:
    """Get list of files to upload, filtered by allowed work IDs."""
    all_files = list(source_dir.glob("*.txt"))
    logger.info(f"Found {len(all_files)} files in {source_dir}")

    files = []
    skipped_copyright = 0
    for p in all_files:
        # Filename format: <work_id>.utf8.txt
        # Extract work_id
        work_id = p.name.split(".")[0]
        if work_id in allowed_ids:
            files.append(p)
        else:
            skipped_copyright += 1

    logger.info(f"Targeting {len(files)} files (Skipped {skipped_copyright} due to copyright)")
    return files


def run_audit(client: object, bucket_name: str, allowed_ids: set[str]):
    """Audit existing files in R2 for copyright violations."""
    logger.info("Starting audit of existing R2 files...")
    # client is explicitly typed as object to avoid ANN401
    paginator = client.get_paginator("list_objects_v2")  # type: ignore
    pages = paginator.paginate(Bucket=bucket_name)

    violation_count = 0
    checked_count = 0

    for page in pages:
        if "Contents" not in page:
            continue

        for obj in page["Contents"]:
            key = obj["Key"]
            checked_count += 1
            # Assumes format <work_id>.utf8.txt
            work_id = key.split(".")[0]

            if work_id not in allowed_ids:
                logger.warning(f"Copyright Violation Found: {key} (ID: {work_id})")
                violation_count += 1

    logger.info(f"Audit complete. Checked {checked_count} files.")
    if violation_count == 0:
        logger.info("No copyright violations found in R2.")
    else:
        logger.warning(f"Found {violation_count} files causing copyright violations.")


def run_concurrent_uploads(
    client: object, files: list[Path], bucket_name: str, max_workers: int, dry_run: bool
):
    """Upload files concurrently."""
    success_count = 0
    failure_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(upload_file, client, file_path, bucket_name, dry_run): file_path
            for file_path in files
        }

        for future in as_completed(futures):
            if future.result():
                success_count += 1
            else:
                failure_count += 1

    logger.info("Upload processing complete.")
    logger.info(f"Success: {success_count}, Failures: {failure_count}")


def main():
    """Upload files to R2."""
    import argparse

    parser = argparse.ArgumentParser(description="Upload files to Cloudflare R2")
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate uploads without actually doing them"
    )
    parser.add_argument("--limit", type=int, help="Limit the number of files to upload")
    parser.add_argument(
        "--audit", action="store_true", help="Audit existing files in R2 for copyright violations"
    )
    args = parser.parse_args()

    try:
        client = get_r2_client()
    except ValueError:
        return

    source_path = Path(SOURCE_DIR)
    if not source_path.exists():
        logger.error(f"Source directory '{SOURCE_DIR}' does not exist.")
        return

    # Load allowed IDs
    csv_path = Path("list_person_all_extended_utf8.csv")
    allowed_ids = load_allowed_work_ids(csv_path)

    if args.audit:
        run_audit(client, R2_BUCKET_NAME, allowed_ids)
        return

    # Get files to upload
    files = get_filtered_files(source_path, allowed_ids)

    if args.limit:
        files = files[: args.limit]
        logger.info(f"Limiting to {args.limit} files")

    # Run uploads
    run_concurrent_uploads(client, files, R2_BUCKET_NAME, MAX_WORKERS, args.dry_run)


if __name__ == "__main__":
    main()
