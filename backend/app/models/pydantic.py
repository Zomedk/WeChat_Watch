from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

class SubscriptionCreate(BaseModel):
    name: str
    fakeid: Optional[str] = None

class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class SubscriptionResponse(BaseModel):
    id: int
    name: str
    fakeid: str
    status: str
    added_at: datetime
    last_sync_at: Optional[datetime] = None
    class Config: from_attributes = True

class ArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    publish_date: date
    digest: Optional[str] = None
    summary: Optional[str] = None
    is_read: bool
    subscription_name: Optional[str] = None
    created_at: datetime
    class Config: from_attributes = True

class AIConfigUpdate(BaseModel):
    api_key: str
    api_base_url: str
    model: str
    proxy: Optional[str] = None
