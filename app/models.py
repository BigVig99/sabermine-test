from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base
import datetime

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(Integer, nullable=False)
    due_date = Column(DateTime, nullable=False)
    completed = Column(Boolean, default=False)