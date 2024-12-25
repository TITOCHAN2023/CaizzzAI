from .base import BaseSchema
from .podcastfy_session import PodcastfySessionSchema
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

class PodcastfyConversationSchema(BaseSchema):
    __tablename__ = "podcastfy_conversation"
    cid: int = Column(Integer, primary_key=True, autoincrement=True)
    sid: int = Column(Integer, ForeignKey(PodcastfySessionSchema.sid, ondelete="CASCADE"), nullable=False)
    create_at: datetime = Column(DateTime, default=datetime.now)
    content_1: str = Column(String(255), nullable=False)
    content_2: str = Column(String(255), nullable=True)
