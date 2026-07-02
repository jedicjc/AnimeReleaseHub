from datetime import datetime
from sqlalchemy import Column, Float, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Anime(Base):
    __tablename__ = "anime"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    status = Column(String, default="announced")
    release_season = Column(String, nullable=True)
    release_year = Column(Integer, nullable=True)
    streaming_platform = Column(String, nullable=True)
    english_dub_status = Column(String, default="unknown")
    source_url = Column(String, nullable=True)

    poster_url = Column(String, nullable=True)
    synopsis = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    genres = Column(String, nullable=True)
    japanese_title = Column(String, nullable=True)
    anime_type = Column(String, nullable=True)
    episodes = Column(Integer, nullable=True)
    rating = Column(String, nullable=True)
    studio = Column(String, nullable=True)
    trailer_url = Column(String, nullable=True)
    members = Column(Integer, nullable=True)
    favorites = Column(Integer, nullable=True)
    popularity = Column(Integer, nullable=True)
    rank = Column(Integer, nullable=True)
    aired_from = Column(String, nullable=True)
    aired_to = Column(String, nullable=True)
    trend_score = Column(Float, default=0)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    category = Column(String, default="general")
    summary = Column(Text, nullable=True)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnimeTrendHistory(Base):
    __tablename__ = "anime_trend_history"

    id = Column(Integer, primary_key=True, index=True)
    anime_id = Column(Integer, nullable=False)

    trend_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
