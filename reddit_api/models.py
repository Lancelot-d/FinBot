"""SQLAlchemy models for Reddit data storage."""

from sqlalchemy import Column, String, Text, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RedditPost(Base):  # pylint: disable=too-few-public-methods
    """SQLAlchemy model for Reddit posts.

    Attributes:
        id: Unique post identifier (MD5 hash).
        content_str: The post content including comments.
        date_insertion: Timestamp of when the post was inserted.
    """

    __tablename__ = "reddit_posts"
    id = Column(String(100), primary_key=True)
    content_str = Column(Text)
    date_insertion = Column(TIMESTAMP, nullable=False)
