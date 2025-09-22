import datetime

from pydantic import BaseModel


class RedirectItem(BaseModel):
    url: str
    # The rest of the fields can be filled with partial data available from the redirect page
    main_title: str | None = None
    title: str | None = None
    description: str | None = None
    published_at: datetime.date | None = None
    created_at: datetime.date | None = None
    last_modified_at: datetime.date | None = None


class ContentItem(BaseModel):
    url: str
    main_title: str
    title: str
    description: str | None = None
    published_at: datetime.date | None = None
    created_at: datetime.date | None = None
    last_modified_at: datetime.date | None = None

    def merge_with_redirect(self, redirect: RedirectItem) -> "ContentItem":
        """Merge current ContentItem with data from a RedirectItem, preferring existing values."""
        return ContentItem(
            url=self.url,
            main_title=self.main_title,
            title=self.title,
            description=self.description or redirect.description,
            published_at=self.published_at or redirect.published_at,
            created_at=self.created_at or redirect.created_at,
            last_modified_at=self.last_modified_at or redirect.last_modified_at,
        )
