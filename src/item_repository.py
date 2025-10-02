import logging

import pandas as pd

from src.models import ContentItem


class ItemRepository:
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> "ItemRepository":
        """Create a new repository from a DataFrame."""
        items = []
        for _, row in df.iterrows():
            row_dict = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
            item = ContentItem(
                url=str(row_dict["url"]),
                main_title=str(row_dict["main_title"]),
                title=str(row_dict["title"]),
                description=row_dict.get("description"),
                published_at=row_dict.get("published_at"),
                created_at=row_dict.get("created_at"),
                last_modified_at=row_dict.get("last_modified_at"),
            )
            items.append(item)
        return cls(items)

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
            # Ensure the columns are in the correct order
            columns=[
                "url",
                "main_title",
                "title",
                "description",
                "attachment_url",
                "published_at",
                "created_at",
                "last_modified_at",
            ],
            data=[item.model_dump() for item in self._items],
        )
