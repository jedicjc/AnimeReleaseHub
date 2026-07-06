import os
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    backend_dir = Path(__file__).resolve().parents[2]
    DATABASE_URL = f"sqlite:///{(backend_dir / 'anime.db').as_posix()}"

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_anime_metadata_columns():
    inspector = inspect(engine)

    if "anime" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("anime")
    }

    column_specs = {
        "japanese_title": "TEXT",
        "anime_type": "TEXT",
        "episodes": "INTEGER",
        "rating": "TEXT",
        "studio": "TEXT",
        "trailer_url": "TEXT",
        "members": "INTEGER",
        "favorites": "INTEGER",
        "popularity": "INTEGER",
        "rank": "INTEGER",
        "aired_from": "TEXT",
        "aired_to": "TEXT",
        "trend_score": "FLOAT DEFAULT 0",
        "maple_score": "FLOAT DEFAULT 0",
    }

    missing_columns = [
        (name, spec)
        for name, spec in column_specs.items()
        if name not in existing_columns
    ]

    if not missing_columns:
        return

    with engine.begin() as connection:
        for name, spec in missing_columns:
            connection.execute(
                text(f'ALTER TABLE anime ADD COLUMN "{name}" {spec}')
            )


def ensure_news_article_columns():
    inspector = inspect(engine)

    if "news_articles" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("news_articles")
    }

    column_specs = {
        "anime_id": "INTEGER",
    }

    missing_columns = [
        (name, spec)
        for name, spec in column_specs.items()
        if name not in existing_columns
    ]

    if not missing_columns:
        return

    with engine.begin() as connection:
        for name, spec in missing_columns:
            connection.execute(
                text(f'ALTER TABLE news_articles ADD COLUMN "{name}" {spec}')
            )


def ensure_news_intelligence_columns():
    inspector = inspect(engine)

    if "news_articles" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("news_articles")
    }

    column_specs = {
        "intelligence_category": "VARCHAR",
        "intelligence_importance": "INTEGER",
        "intelligence_event": "VARCHAR",
        "intelligence_anime": "VARCHAR",
        "intelligence_summary": "TEXT",
    }

    missing_columns = [
        (name, spec)
        for name, spec in column_specs.items()
        if name not in existing_columns
    ]

    if not missing_columns:
        return

    with engine.begin() as connection:
        for name, spec in missing_columns:
            connection.execute(
                text(f'ALTER TABLE news_articles ADD COLUMN "{name}" {spec}')
            )
