from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import hashlib


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

        self.con = self.engine.connect()

        """
        try:
            self.con.execute(text("CREATE TABLE reddit_posts (id VARCHAR2(100 CHAR) PRIMARY KEY, content_str CLOB, date_insertion TIMESTAMP DEFAULT SYSTIMESTAMP);"))
            self.con.commit()
        except Exception as e:
            print(e)
            self.con.rollback()
        """

        self.con.commit()

    def add_reddit_post(self, content_str: str, title: str, author: str):
        try:
            # Generate a unique ID by creating a hash of title and author
            post_id = self.generate_post_id(title=title, author=author)

            # Insert data into the table
            self.con.execute(
                text(
                    """
                    INSERT INTO reddit_posts (id, content_str, date_insertion)
                    VALUES (:id, :content_str, CURRENT_TIMESTAMP)
                """
                ),
                {"id": post_id, "content_str": content_str},
            )
            self.con.commit()

        except Exception as e:
            self.con.rollback()
            if (
                getattr(e, "code", None) != "gkpj"
            ):  # Check if the exception has a specific code
                print(e)

    def get_reddit_posts(self):
        # Fetch all posts from the database
        result = self.con.execute(text("SELECT * FROM reddit_posts")).fetchall()
        return result

    def is_reddit_post_in_db(self, post_id: str) -> bool:
        # Query the database to check if the post ID exists
        result = self.con.execute(
            text("SELECT 1 FROM reddit_posts WHERE id = :id FETCH FIRST 1 ROWS ONLY"),
            {"id": post_id},  # Directly checking the ID
        ).fetchone()

        return result is not None

    def generate_post_id(self, title: str, author: str) -> str:
        # Generate a unique post ID based on title and author
        return hashlib.md5(f"{title}{author}".encode("utf-8")).hexdigest()
