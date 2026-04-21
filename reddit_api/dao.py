"""Data Access Object (DAO) for managing Reddit posts in Oracle database."""

import os
import hashlib

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from models import RedditPost
from logger_config import logger

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
        logger.info("Initializing DAO and Oracle connection")
        password = os.getenv("ORACLE_PASSWORD")
        dsn = os.getenv("ORACLE_DSN")
        user = os.getenv("ORACLE_USER")
        self.engine = create_engine(
            "oracle+oracledb://:@",
            connect_args={"user": user, "password": password, "dsn": dsn},
        )
        Base.metadata.create_all(self.engine)
        self._ensure_extracted_information_column()
        self.session_maker = sessionmaker(bind=self.engine)
        logger.info("DAO initialized and database metadata ensured")

    def _ensure_extracted_information_column(self) -> None:
        """Ensure reddit_posts.extracted_information exists for existing databases."""
        query = text(
            """
            SELECT COUNT(*)
            FROM user_tab_columns
            WHERE table_name = 'REDDIT_POSTS'
              AND column_name = 'EXTRACTED_INFORMATION'
            """
        )
        alter = text("ALTER TABLE reddit_posts ADD (extracted_information CLOB)")

        with self.engine.begin() as connection:
            exists = int(connection.execute(query).scalar() or 0)
            if exists == 0:
                connection.execute(alter)
                logger.info("Added missing column reddit_posts.extracted_information")

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
            logger.info("Inserted reddit post id=%s", post_id)
        except (ValueError, KeyError, AttributeError):
            session.rollback()
            logger.exception("Failed to insert reddit post")
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
            logger.info("Fetched %d reddit posts from database", len(posts))
            return posts
        except (ValueError, KeyError, AttributeError):
            logger.exception("Failed to fetch reddit posts")
            session.rollback()
            return None
        finally:
            session.close()

    def get_reddit_post_ids(self) -> list[str]:
        """Retrieve all reddit post IDs from the database."""
        session = self.session_maker()
        try:
            rows = session.query(RedditPost.id).all()
            ids = [row[0] for row in rows if row[0] is not None]
            logger.info("Fetched %d reddit post IDs from database", len(ids))
            return ids
        except (ValueError, KeyError, AttributeError):
            logger.exception("Failed to fetch reddit post IDs")
            session.rollback()
            return []
        finally:
            session.close()

    def get_reddit_posts_count(self) -> int:
        """Retrieve the total number of reddit posts in the database."""
        session = self.session_maker()
        try:
            count = session.query(RedditPost).count()
            logger.info("Fetched reddit post count=%d", count)
            return count
        except (ValueError, KeyError, AttributeError):
            logger.exception("Failed to fetch reddit post count")
            session.rollback()
            return 0
        finally:
            session.close()

    def get_reddit_posts_by_ids(self, post_ids: list[str]) -> list[tuple[str, str]]:
        """Retrieve reddit post IDs and content for selected IDs."""
        if not post_ids:
            return []

        session = self.session_maker()
        try:
            rows = (
                session.query(RedditPost.id, RedditPost.content_str)
                .filter(RedditPost.id.in_(post_ids))
                .all()
            )
            posts = [(row[0], row[1]) for row in rows if row[0] and row[1]]
            logger.info("Fetched %d reddit posts by ID", len(posts))
            return posts
        except (ValueError, KeyError, AttributeError):
            logger.exception("Failed to fetch reddit posts by IDs")
            session.rollback()
            return []
        finally:
            session.close()

    def get_reddit_posts_missing_extracted_information(
        self, limit: int = 100
    ) -> list[tuple[str, str]]:
        """Fetch posts where extracted_information is still null."""
        session = self.session_maker()
        try:
            rows = (
                session.query(RedditPost.id, RedditPost.content_str)
                .filter(RedditPost.extracted_information.is_(None))
                .filter(RedditPost.content_str.isnot(None))
                .limit(max(limit, 1))
                .all()
            )
            return [(row[0], row[1]) for row in rows if row[0] and row[1]]
        except (ValueError, KeyError, AttributeError):
            logger.exception("Failed to fetch posts missing extracted_information")
            session.rollback()
            return []
        finally:
            session.close()

    def update_reddit_post_extracted_information(
        self, post_id: str, extracted_information: str
    ) -> bool:
        """Persist extracted_information for a post ID."""
        session = self.session_maker()
        try:
            updated_rows = (
                session.query(RedditPost)
                .filter(RedditPost.id == post_id)
                .update({RedditPost.extracted_information: extracted_information})
            )
            session.commit()
            return updated_rows > 0
        except (ValueError, KeyError, AttributeError):
            logger.exception(
                "Failed to update extracted_information for reddit post id=%s", post_id
            )
            session.rollback()
            return False
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
        except (ValueError, KeyError, AttributeError):
            logger.exception("Failed to check reddit post existence for id=%s", post_id)
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
