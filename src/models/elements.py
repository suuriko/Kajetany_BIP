import datetime

from pydantic import BaseModel


class Elements(BaseModel):
    main_title: str
    title: str
    url: str
    published_at: datetime.date | None
    created_at: datetime.date | None
    last_modified_at: datetime.date | None
