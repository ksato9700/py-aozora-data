import logging
from typing import Any

from google.cloud import firestore  # type: ignore

logger = logging.getLogger(__name__)


class AozoraFirestore:
    """Firestore Access Object for Aozora Bunko data."""

    def __init__(self, project_id: str | None = None) -> None:
        """Initialize Firestore client and local caches."""
        self.db = firestore.Client(project=project_id)
        self.batch = self.db.batch()
        self.batch_count = 0
        self.BATCH_LIMIT = 450  # Firestore batch limit is 500

        # Caches to verify uniqueness within the current run
        self.seen_books: set[str] = set()
        self.seen_persons: set[str] = set()
        self.seen_contributors: set[str] = set()

    def get_watermark(self) -> str | None:
        """Get the last processed date from Firestore."""
        doc = self.db.collection("config").document("import_state").get()
        if doc.exists:
            return doc.to_dict().get("last_modified")
        return None

    def save_watermark(self, date_str: str) -> None:
        """Save the last processed date to Firestore."""
        logger.info(f"Saving watermark: {date_str}")
        self.db.collection("config").document("import_state").set({"last_modified": date_str})

    def _flush_batch_if_needed(self, force: bool = False) -> None:
        if self.batch_count >= self.BATCH_LIMIT or (force and self.batch_count > 0):
            logger.info(f"Committing batch of {self.batch_count} operations...")
            self.batch.commit()
            self.batch = self.db.batch()
            self.batch_count = 0

    def upsert_book(self, book_id: str, data: dict[str, Any]):
        """Upsert a book."""
        if book_id not in self.seen_books:
            ref = self.db.collection("books").document(book_id)
            logger.info(f"Upserting book: {book_id}")
            self.batch.set(ref, data, merge=True)
            self.batch_count += 1
            self._flush_batch_if_needed()
            self.seen_books.add(book_id)

    def upsert_person(self, person_id: str, data: dict[str, Any]):
        """Upsert a person."""
        if person_id not in self.seen_persons:
            ref = self.db.collection("persons").document(person_id)
            logger.info(f"Upserting person: {person_id}")
            self.batch.set(ref, data, merge=True)
            self.batch_count += 1
            self._flush_batch_if_needed()
            self.seen_persons.add(person_id)

    def upsert_contributor(self, contributor_id: str, data: dict[str, Any]) -> None:
        """Upsert a contributor."""
        if contributor_id not in self.seen_contributors:
            ref = self.db.collection("contributors").document(contributor_id)
            logger.info(f"Upserting contributor: {contributor_id}")
            self.batch.set(ref, data)
            self.batch_count += 1
            self._flush_batch_if_needed()
            self.seen_contributors.add(contributor_id)

    def commit(self):
        """Force commit remaining batch."""
        self._flush_batch_if_needed(force=True)
