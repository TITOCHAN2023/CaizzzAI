from .base import BaseSchema
from .users import UserSchema
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

class VectorDBSchema(BaseSchema):
    __tablename__ = "VectorDB"
    vdbid: int = Column(Integer, primary_key=True, autoincrement=True)
    uid: int = Column(Integer, ForeignKey(UserSchema.uid, ondelete="CASCADE"), nullable=False)
    name : str = Column(String(255), nullable=False)
    create_at: datetime = Column(DateTime, default=datetime.now)
    update_at: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    index : str = Column(String(255), nullable=True)

