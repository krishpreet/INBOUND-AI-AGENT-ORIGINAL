from sqlalchemy import Column, Integer, String
from app.core.db import Base

class Call(Base):
    __tablename__ = "calls"
    id = Column(Integer, primary_key=True, index=True)
    caller = Column(String, nullable=False)
    receiver = Column(String, nullable=False)
    status = Column(String, default="initiated")