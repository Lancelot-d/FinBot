"""Data Access Object (DAO) for managing Reddit posts in Oracle database."""

import os
import hashlib

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from models import RedditPost

Base = declarative_base()


class Singleton:  # pylint: disable=too-few-public-methods
    """Singleton pattern implementation for ensuring single instance."""

    _instances = {}

    @classmethod
    def get_instance(cls, *args, **kwargs) -> "Singleton":
        """Get or create a singleton instance.

        Args:
            force_refresh: If True, creates a new instance even if one exists.

        Returns:
            The singleton instance of the class.
        """
        force_refresh = kwargs.pop("force_refresh", False)
        if force_refresh or cls not in cls._instances:
            cls._instances[cls] = cls(*args, **kwargs)
        return cls._instances[cls]


class DAO(Singleton):
    """Data Access Object for Reddit posts storage and retrieval."""

    load_dotenv()

    def __init__(self) -> None:
        """Initialize DAO with Oracle database connection."""
        password = os.getenv("PASSWORD")
        # Break long line into multiple lines
        dsn = (
            "(description= (retry_count=20)(retry_delay=3)"
            "(address=(protocol=tcps)(port=1521)(host=adb.ca-montreal-1.oraclecloud.com))"
            "(connect_data=(service_name=g6e3bf2bdf6f8f6_db2_high.adb.oraclecloud.com))"
            "(security=(ssl_server_dn_match=yes)))"
        )
        user = os.getenv("USER")
        self.engine = create_engine(
            "oracle+oracledb://:@",
            connect_args={"user": user, "password": password, "dsn": dsn},
        )
        Base.metadata.create_all(self.engine)
        self.session_maker = sessionmaker(bind=self.engine)

    def add_reddit_post(self, content_str: str, title: str, author: str) -> None:
        """Add a Reddit post to the database.

        Args:
            content_str: The post content as string.
            title: The post title.
            author: The post author.
        """
        from datetime import datetime  # pylint: disable=import-outside-toplevel

        session = self.session_maker()
        try:
            post_id = self.generate_post_id(title=title, author=author)

            post = RedditPost(
                id=post_id, content_str=content_str, date_insertion=datetime.now()
            )
            session.add(post)
            session.commit()
        except (ValueError, KeyError, AttributeError) as e:
            session.rollback()
            print(e)
        finally:
            session.close()

    def get_reddit_posts(self) -> list["RedditPost"] | None:
        """Retrieve all Reddit posts from the database.

        Returns:
            List of RedditPost objects, or None if error occurs.
        """
        session = self.session_maker()
        try:
            posts = session.query(RedditPost).all()
            return posts
        except (ValueError, KeyError, AttributeError) as e:
            print(e)
            session.rollback()
            return None
        finally:
            session.close()

    def is_reddit_post_in_db(self, post_id: str) -> bool:
        """Check if a Reddit post exists in the database.

        Args:
            post_id: The unique post identifier.

        Returns:
            True if post exists, False otherwise.
        """
        session = self.session_maker()
        try:
            exists = session.query(RedditPost).filter_by(id=post_id).first() is not None
            return exists
        except (ValueError, KeyError, AttributeError) as e:
            print(e)
            session.rollback()
            return False
        finally:
            session.close()

    def generate_post_id(self, title: str, author: str) -> str:
        """Generate a unique post ID based on title and author.

        Args:
            title: The post title.
            author: The post author.

        Returns:
            MD5 hash of title and author as post ID.
        """
        # Generate a unique post ID based on title and author
        return hashlib.md5(f"{title}{author}".encode("utf-8")).hexdigest()
