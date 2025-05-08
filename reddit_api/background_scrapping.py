import yars
from dao import DAO
from cleantext import clean

dao = None

def clean_post(post : list[str]):
    #pip Clean-text
    clear_post = [clean(text=p, extra_spaces=True) for p in post]
    #Remove one word post
    clear_post = [p for p in clear_post if " " in p]
    #Remove too short post
    clear_post = [p for p in clear_post if len(p)>=30]
    #Remove [deleted]
    clear_post = [p for p in clear_post if "[deleted]" not in p]
    
    return clear_post

def fetch_post_details(miner : yars.YARS, permalink : str):
    """Récupère les détails d'un post."""
    return miner.scrape_post_details(permalink)


def process_subreddit_posts(miner : yars.YARS, category : list, reddit : str = "JustBuyXEQT"):
    """Traite les posts d'une catégorie."""
    miner.change_user_agent()
    subreddit_posts = miner.fetch_subreddit_posts(reddit, limit=100, category=category, time_filter="all")
    
    for post_data in subreddit_posts:
        if not dao.is_reddit_post_in_db(dao.generate_post_id(title=post_data["title"], author=post_data["author"])):
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
            dao.add_reddit_post(content_str=joined_post,title=post_data["title"], author=post_data["author"])
            print("Inserted one post")
        else:
            pass
            #print("Already in db")
            
def get_replies(comment, post):
    """Function to recursively get all replies (sub-comments)"""
    if "replies" in comment:
        for rep in comment["replies"]:
            post.append(rep["body"])
            # Recursively process replies of replies
            get_replies(rep, post)
            
def run():
    """Lance le traitement des catégories."""
    categories = ["hot", "top"]
    sub = ["PersonalFinanceCanada", "JustBuyXEQT", "QuebecFinance", "fican", "dividendscanada", "Wealthsimple", "PersonalFinanceCanada", "CanadianInvestor"]
    miner = yars.YARS()
    
    global dao
    dao = DAO.get_instance(force_refresh=True)
    
    for s in sub:
        print(f"""Scrapping {s}""")
        for category in categories:
            print(f"""Category {category} starting""")
            process_subreddit_posts(reddit=s, miner=miner, category=category)
            print(f"""Category {category} processed""")
            
    print("Scrap processed")