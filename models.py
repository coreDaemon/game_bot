from sqlalchemy import Column, Integer, String, Float
from database import Base


class TrackedGame(Base):
    __tablename__ = "tracked_games"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(String, unique=True, index=True)
    name = Column(String)
    current_price = Column(Float)
    chat_id = Column(Integer)