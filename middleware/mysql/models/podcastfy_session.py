from .base import BaseSchema
from .users import UserSchema
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

class PodcastfySessionSchema(BaseSchema):
    __tablename__ = "podcastfy_session"
    sid: int = Column(Integer, primary_key=True, autoincrement=True)
    uid: int = Column(Integer, ForeignKey(UserSchema.uid, ondelete="CASCADE"), nullable=False)
    sessionname: str = Column(String(255), nullable=False)
    create_at: datetime = Column(DateTime, default=datetime.now)