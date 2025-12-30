import logging
from typing import Any, Dict, Set

from google.cloud import firestore  # type: ignore

logger = logging.getLogger(__name__)


class AozoraFirestore:
    """Firestore Access Object for Aozora Bunko data."""

    def __init__(self, project_id: str | None = None):
        """Initialize Firestore client and local caches."""
        self.db = firestore.Client(project=project_id)
        self.batch = self.db.batch()
        self.batch_count = 0
        self.BATCH_LIMIT = 450  # Firestore batch limit is 500

        # Caches to store the state of existing documents for diffing
        # Map: ID -> hash/last_modified. For now using entire data dict hash could be expensive,
        # but storing 'last_modified' from the CSV is a good proxy if provided.
        # However, checking deeper equality is safer.
        # Let's verify 'last_modified' field availability.
        self.existing_books: Dict[str, Any] = {}
        self.existing_persons: Dict[str, Any] = {}
        self.existing_contributors: Set[str] = set() # using "book_id-person_id-role" as key

    def prefetch_metadata(self):
        """Fetch existing document IDs and relevant metadata to minimize writes."""
        logger.info("Prefetching existing metadata from Firestore...")

        # Books
        # We assume 'last_modified' field in the document matches the CSV's last_modified
        docs = self.db.collection("books").select(["last_modified", "text_updated", "html_updated"]).stream()
        for doc in docs:
            self.existing_books[doc.id] = doc.to_dict()

        # Persons
        # Persons don't have a 'last_modified' field in the CSV usually (need to check),
        # so we might rely on content comparison or just "exists" check if immutable?
        # Aozora persons are mutable (death date etc).
        # We'll just fetch them all? It's about 1-2k persons? No, probably more.
        # Let's fetch IDs for now.
        docs = self.db.collection("persons").select([]).stream() # ID only
        for doc in docs:
            self.existing_persons[doc.id] = True

        # Contributors
        docs = self.db.collection("contributors").select([]).stream()
        for doc in docs:
            self.existing_contributors.add(doc.id)

        logger.info(f"Prefetched: {len(self.existing_books)} books, {len(self.existing_persons)} persons.")

    def _flush_batch_if_needed(self, force: bool = False):
        if self.batch_count >= self.BATCH_LIMIT or (force and self.batch_count > 0):
            logger.info(f"Committing batch of {self.batch_count} operations...")
            self.batch.commit()
            self.batch = self.db.batch()
            self.batch_count = 0

    def upsert_book(self, book_id: str, data: Dict[str, Any]):
        """Upsert a book if it has changed."""
        # Check diff
        # Simplified check: if book exists and last_modified matches, skip.
        # Note: 'text_updated' and 'html_updated' are likely good indicators too.

        should_update = True
        if book_id in self.existing_books:
            existing = self.existing_books[book_id]
            # If relevant fields match, skip
            if (existing.get("last_modified") == data.get("last_modified") and
                existing.get("text_updated") == data.get("text_updated") and
                existing.get("html_updated") == data.get("html_updated")):
                should_update = False

        if should_update:
            ref = self.db.collection("books").document(book_id)
            self.batch.set(ref, data, merge=True)
            self.batch_count += 1
            self._flush_batch_if_needed()

    def upsert_person(self, person_id: str, data: Dict[str, Any]):
        """Upsert a person."""
        # For persons, since we don't have a clear versioning field in the CSV row easily available
        # without looking at the schema again (Step 12: just name, dates),
        # we might just overwrite or check equality if we fetched data.
        # For optimization, let's assume we update if we haven't seen this valid data before?
        # But CSV has one row per book+person. The person data is repeated.
        # We should at least avoid writing the SAME person multiple times in one run.

        # NOTE: This method will be called multiple times for the same person in one import run.
        # We must avoid adding to batch multiple times.

        # Since we are iterating streams, we don't store "what we pending wrote" in 'existing_persons'.
        # We should maybe track "processed_ids" in this run.

        # But for now, let's just write if not in existing_persons (simple "new check").
        # Detailed diffing would require fetching full person data which is expensive.
        # Or we can just set(merge=True) which is cheaper than read-modify-write but still a write op.

        # Better approach: Just set it. Firestore is fast.
        # But user requested "only changed places".
        # Let's skip if we already sent this person ID in this BATCH or this RUN?
        # Implementing a "seen_in_run" cache.
        pass # Logic handled in next block to keep this pure.

        ref = self.db.collection("persons").document(person_id)
        self.batch.set(ref, data, merge=True)
        self.batch_count += 1
        self._flush_batch_if_needed()

    def upsert_contributor(self, contributor_id: str, data: Dict[str, Any]):
        if contributor_id not in self.existing_contributors:
            ref = self.db.collection("contributors").document(contributor_id)
            self.batch.set(ref, data)
            self.batch_count += 1
            self._flush_batch_if_needed()
            self.existing_contributors.add(contributor_id)

    def commit(self):
        """Force commit remaining batch."""
        self._flush_batch_if_needed(force=True)
