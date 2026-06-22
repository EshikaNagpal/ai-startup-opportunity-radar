import requests
import json
import time

TOP_STORIES_URL = (
    "https://hacker-news.firebaseio.com/v0/topstories.json"
)

story_ids = requests.get(
    TOP_STORIES_URL
).json()

posts = []

for story_id in story_ids[:50]:

    try:

        story = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        ).json()

        posts.append({
            "source": "hackernews",
            "title": story.get("title", ""),
            "text": story.get("text", ""),
            "score": story.get("score", 0),
            "comments": story.get("descendants", 0),
            "url": story.get("url", "")
        })

        time.sleep(0.1)

    except Exception:
        pass

with open(
    "data/live/hn_posts.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        posts,
        f,
        indent=2
    )