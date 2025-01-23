import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String


from .base import BaseSchema
from .users import UserSchema



class audioPositionSchema(BaseSchema):


    __tablename__ = "audio_position"
    audio_id: int = Column(Integer, primary_key=True, autoincrement=True)
    create_at: datetime = Column(DateTime, default=datetime.datetime.now)
    audio_content: str = Column(String(2048), nullable=False)
    audio_position: str = Column(String(512), nullable=False)
    uid: int = Column(Integer, ForeignKey(UserSchema.uid, ondelete="CASCADE"), nullable=False)
