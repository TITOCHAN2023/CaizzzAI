from .base import BaseSchema
from .session import SessionSchema

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

class historySchema(BaseSchema):
    __tablename__ = "history"
    hid: int = Column(Integer, primary_key=True, autoincrement=True)
    sid: int = Column(Integer, ForeignKey(SessionSchema.sid, ondelete="CASCADE"), nullable=False)
    create_at: datetime = Column(DateTime, default=datetime.now)
    update_at: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    delete_at: datetime = Column(DateTime, nullable=True)
    is_deleted: bool = Column(Boolean, nullable=False, default=False)
    is_logout: bool = Column(Boolean, nullable=False, default=False)
    ip: str = Column(String(255), nullable=False)
    user_agent: str = Column(String(255), nullable=False)
    last_active: datetime = Column(DateTime, nullable=False, default=datetime.now)