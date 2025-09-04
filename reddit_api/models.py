from sqlalchemy import Column, String, Text, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class RedditPost(Base):
    __tablename__ = 'reddit_posts'
    id = Column(String(100), primary_key=True)
    content_str = Column(Text)
    date_insertion = Column(TIMESTAMP, nullable=False)