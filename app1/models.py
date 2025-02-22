from sqlalchemy import Column, Integer, String, DateTime, Text, CheckConstraint
from .database import Base
import datetime

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    question = Column(String(1000), nullable=False)
    answer = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('length(question) > 0', name='question_not_empty'),
        CheckConstraint('length(session_id) > 0', name='session_id_not_empty'),
    ) 