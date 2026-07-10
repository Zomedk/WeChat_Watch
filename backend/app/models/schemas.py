from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Date
from sqlalchemy.sql import func
from app.models.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    fakeid = Column(String(100), nullable=False, unique=True)
    status = Column(String(20), default="active")
    added_at = Column(DateTime, server_default=func.now())
    last_sync_at = Column(DateTime)

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    publish_date = Column(Date, nullable=False)
    digest = Column(Text)
    content = Column(Text)
    summary = Column(Text)
    markdown_path = Column(String(500))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class SettingsModel(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
