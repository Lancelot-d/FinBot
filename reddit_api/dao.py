from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from models import RedditPost
import hashlib

Base = declarative_base()


class Singleton:
    _instances = {}

    @classmethod
    def get_instance(cls, *args, **kwargs):
        force_refresh = kwargs.pop("force_refresh", False)
        if force_refresh or cls not in cls._instances:
            cls._instances[cls] = cls(*args, **kwargs)
        return cls._instances[cls]


class DAO(Singleton):
    load_dotenv()

    def __init__(self) -> None:
        PASSWORD = os.getenv("PASSWORD")
        DSN = "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.ca-montreal-1.oraclecloud.com))(connect_data=(service_name=g6e3bf2bdf6f8f6_db2_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"
        USER = os.getenv("USER")
        self.engine = create_engine(
            f"oracle+oracledb://:@",
            connect_args={"user": USER, "password": PASSWORD, "dsn": DSN},
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_reddit_post(self, content_str: str, title: str, author: str):
        session = self.Session()
        try:
            post_id = self.generate_post_id(title=title, author=author)
            from datetime import datetime

            post = RedditPost(
                id=post_id, content_str=content_str, date_insertion=datetime.now()
            )
            session.add(post)
            session.commit()
        except Exception as e:
            session.rollback()
            print(e)
        finally:
            session.close()

    def get_reddit_posts(self):
        session = self.Session()
        try:
            posts = session.query(RedditPost).all()
            return posts
        except Exception as e:
            print(e)
            session.rollback()
        finally:
            session.close()

    def is_reddit_post_in_db(self, post_id: str) -> bool:
        session = self.Session()
        try:
            exists = session.query(RedditPost).filter_by(id=post_id).first() is not None
            return exists
        except Exception as e:
            print(e)
            session.rollback()
        finally:
            session.close()

    def generate_post_id(self, title: str, author: str) -> str:
        # Generate a unique post ID based on title and author
        return hashlib.md5(f"{title}{author}".encode("utf-8")).hexdigest()
