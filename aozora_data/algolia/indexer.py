import logging
import os

from algoliasearch.search.client import SearchClientSync

logger = logging.getLogger(__name__)

BATCH_SIZE = 500


class AlgoliaIndexer:
    """Indexes books and persons into Algolia after a Firestore import run."""

    def __init__(self) -> None:
        """Initialise Algolia client from environment variables."""
        app_id = os.environ["ALGOLIA_APP_ID"]
        admin_key = os.environ["ALGOLIA_ADMIN_KEY"]
        self._client = SearchClientSync(app_id, admin_key)

    def index_books(self, records: list[dict]) -> None:
        """Upload book records to the Algolia 'books' index."""
        if not records:
            return
        logger.info(f"Indexing {len(records)} book(s) to Algolia...")
        for i in range(0, len(records), BATCH_SIZE):
            self._client.save_objects(index_name="books", objects=records[i : i + BATCH_SIZE])
        logger.info("Book indexing done.")

    def index_persons(self, records: list[dict]) -> None:
        """Upload person records to the Algolia 'persons' index."""
        if not records:
            return
        logger.info(f"Indexing {len(records)} person(s) to Algolia...")
        for i in range(0, len(records), BATCH_SIZE):
            self._client.save_objects(index_name="persons", objects=records[i : i + BATCH_SIZE])
        logger.info("Person indexing done.")
