import logging

import pandas as pd

from src.models import ContentItem


class ItemRepository:
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> "ItemRepository":
        """Create a new repository from a DataFrame."""
        try:
            items = [ContentItem(**row.to_dict()) for _, row in df.iterrows()]
            return cls(items)
        except Exception as e:
            logging.getLogger("item_repository").error(f"Failed to create repository from DataFrame: {e}")
            raise ValueError(f"Invalid DataFrame structure: {e}") from e

    def __init__(self, items: list[ContentItem] | None = None):
        self.logger = logging.getLogger("item_repository")
        self._items: list[ContentItem] = []

        if items:
            self.add_items(items)

    @property
    def items(self) -> list[ContentItem]:
        """Get all items (read-only access)."""
        return self._items.copy()

    @property
    def count(self) -> int:
        """Get the number of items in the repository."""
        return len(self._items)

    def add_item(self, item: ContentItem) -> bool:
        """Add an item to the repository. Returns True if added, False if duplicate."""
        if not self.exists(item):
            self._items.append(item)
            self.logger.debug(f"Item added: {item.url}")
            return True
        else:
            self.logger.debug(f"Duplicate item ignored: {item.url}")
            return False

    def exists(self, item: ContentItem) -> bool:
        """Check if an item exists by comparing all fields."""
        return any(existing_item == item for existing_item in self._items)

    def add_items(self, items: list[ContentItem]) -> int:
        """Add multiple items. Returns count of items actually added."""
        added_count = 0
        for item in items:
            if self.add_item(item):
                added_count += 1
        return added_count

    def clear(self) -> None:
        """Clear all items from the repository."""
        self._items.clear()
        self.logger.debug("All items cleared from repository")

    def to_dataframe(self) -> pd.DataFrame:
        """Convert repository items to a DataFrame."""
        return pd.DataFrame(
            columns=list(ContentItem.model_fields.keys()), data=[item.model_dump() for item in self._items]
        )
