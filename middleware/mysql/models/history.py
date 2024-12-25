from .base import BaseSchema
from .chat_session import ChatSessionSchema

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

class historySchema(BaseSchema):
    __tablename__ = "history"
    hid: int = Column(Integer, primary_key=True, autoincrement=True)
    sid: int = Column(Integer, ForeignKey(ChatSessionSchema.sid, ondelete="CASCADE"), nullable=False)
    create_at: datetime = Column(DateTime, default=datetime.now())
    is_deleted: bool = Column(Boolean, nullable=False, default=False)
    ip: str = Column(String(255), nullable=False)
    user_api_key: str = Column(String(255), nullable=False)
    user_base_url: str = Column(String(255), nullable=False,default="https://api.openai-proxy.org/v1")
    llm_model: str = Column(String(255), nullable=False,default="gpt-4o-mini")
    usermessage: str = Column(String(4096), nullable=False)
    botmessage: str = Column(String(4096), nullable=False)