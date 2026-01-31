"""Background scraping module for collecting Reddit posts."""

from dao import DAO
from cleantext import clean
from scrapping import yars

# Module-level DAO instance (initialized in run())
DAO_INSTANCE = None  # pylint: disable=invalid-name


def clean_post(post: list[str]) -> list[str]:
    """Clean and filter Reddit posts.

    Args:
        post: List of post text strings.

    Returns:
        List of cleaned post strings.
    """
    # pip Clean-text
    clear_post = [clean(text=p, extra_spaces=True) for p in post]
    # Remove one word post
    clear_post = [p for p in clear_post if " " in p]
    # Remove too short post
    clear_post = [p for p in clear_post if len(p) >= 30]
    # Remove [deleted]
    clear_post = [p for p in clear_post if "[deleted]" not in p]

    return clear_post


def fetch_post_details(miner: yars.YARS, permalink: str) -> dict:
    """Fetch details for a specific post.

    Args:
        miner: YARS instance for scraping.
        permalink: The post permalink.

    Returns:
        Post details dictionary.
    """
    return miner.scrape_post_details(permalink)


def process_subreddit_posts(
    miner: yars.YARS, category: str, reddit: str = "JustBuyXEQT"
) -> None:
    """Process posts from a subreddit category.

    Args:
        miner: YARS instance for scraping.
        category: List of category types to scrape.
        reddit: Subreddit name.
    """
    miner.change_user_agent()
    subreddit_posts = miner.fetch_subreddit_posts(
        reddit, limit=100, category=category, time_filter="all"
    )

    for post_data in subreddit_posts:
        if not DAO_INSTANCE.is_reddit_post_in_db(
            DAO_INSTANCE.generate_post_id(
                title=post_data["title"], author=post_data["author"]
            )
        ):
            post_details = fetch_post_details(miner, post_data["permalink"])
            post = []

            # Adding the post title and body
            if "body" in post_details:
                post.append(post_details["title"] + post_details["body"])

            # Recursively add comments and replies
            if "comments" in post_details:
                for comment in post_details["comments"]:
                    post.append(comment["body"])
                    # Recursively add replies
                    get_replies(comment, post)

            joined_post = "\n Next comment : ".join(clean_post(post))
            DAO_INSTANCE.add_reddit_post(
                content_str=joined_post,
                title=post_data["title"],
                author=post_data["author"],
            )


def get_replies(comment: dict, post: list[str]) -> None:
    """Recursively extract all replies (sub-comments) from a comment.

    Args:
        comment: Comment dictionary containing replies.
        post: List to append reply bodies to.
    """
    if "replies" in comment:
        for rep in comment["replies"]:
            post.append(rep["body"])
            # Recursively process replies of replies
            get_replies(rep, post)


def run() -> None:
    """Run the background scraping process for all configured subreddits."""
    categories = ["hot", "top"]
    sub = [
        "PersonalFinanceCanada",
        "JustBuyXEQT",
        "QuebecFinance",
        "fican",
        "dividendscanada",
        "Wealthsimple",
        "PersonalFinanceCanada",
        "CanadianInvestor",
    ]
    miner = yars.YARS()

    global DAO_INSTANCE  # pylint: disable=global-statement
    DAO_INSTANCE = DAO.get_instance(force_refresh=True)

    for s in sub:
        for category in categories:
            process_subreddit_posts(reddit=s, miner=miner, category=category)
            print(f"""Category {category} processed""")

    print("Scrap processed")
