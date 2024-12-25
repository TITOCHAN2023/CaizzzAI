from .base import BaseSchema
from .users import UserSchema
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

class ChatSessionSchema(BaseSchema):
    __tablename__ = "session"
    sid: int = Column(Integer, primary_key=True, autoincrement=True)
    uid: int = Column(Integer, ForeignKey(UserSchema.uid, ondelete="CASCADE"), nullable=False)
    sessionname: str = Column(String(255), nullable=False,default="unnamedSession")
    create_at: datetime = Column(DateTime, default=datetime.now)
    update_at: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    delete_at: datetime = Column(DateTime, nullable=True)
    last_active: datetime = Column(DateTime, nullable=False, default=datetime.now)