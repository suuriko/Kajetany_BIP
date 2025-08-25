from pydantic import BaseModel 
import datetime

class Elements(BaseModel):
    main_title: str
    title: str
    url: str
    published_at: datetime.date | None