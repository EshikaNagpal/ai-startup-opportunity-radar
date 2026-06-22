import requests
import json

SUBREDDITS = [
    "entrepreneur",
    "smallbusiness",
    "freelance",
    "startups"
]

posts = []

for subreddit in SUBREDDITS:

    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=25"

    headers = {
        "User-Agent": "FounderIntelligence/1.0"
    }

    response = requests.get(
        url,
        headers=headers
    )

    data = response.json()

    for post in data["data"]["children"]:

        p = post["data"]

        posts.append({
            "source": "reddit",
            "subreddit": subreddit,
            "title": p["title"],
            "text": p["selftext"],
            "score": p["score"],
            "comments": p["num_comments"],
            "created": p["created_utc"]
        })

with open(
    "data/live/reddit_posts.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        posts,
        f,
        indent=2
    )