from reddit_api.dao import DAO

def test_dao():
    dao = DAO.get_instance()
    posts = dao.get_reddit_posts()
    assert len(posts) > 0, "No Reddit posts found in the database."
    print(f"Retrieved {len(posts)} Reddit posts from the database.")

if __name__ == "__main__":
    test_dao()