import streamlit as st
import json


def save_opportunity(post):

    try:

        with open(
            "data/live/saved_opportunities.json",
            "r",
            encoding="utf-8"
        ) as f:

            saved = json.load(f)

    except:

        saved = []

    already_exists = any(
    p.get("title") == post.get("title")
    for p in saved
)

    if not already_exists:
        saved.append(post)

    with open(
        "data/live/saved_opportunities.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            saved,
            f,
            indent=2,
            ensure_ascii=False
        )

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Live Discovery",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Live Discovery")
st.caption(
    "Discover startup opportunities from real-world discussions."
)

# =====================================
# LOAD DATA
# =====================================

posts = []

# =========================
# REDDIT
# =========================

try:
    with open(
        "data/live/reddit_posts.json",
        "r",
        encoding="utf-8"
    ) as f:

        posts.extend(
            json.load(f)
        )

except FileNotFoundError:

    st.warning(
        "reddit_posts.json not found."
    )

# =========================
# HACKER NEWS
# =========================

try:
    with open(
        "data/live/hn_posts.json",
        "r",
        encoding="utf-8"
    ) as f:

        posts.extend(
            json.load(f)
        )

except FileNotFoundError:

    st.warning(
        "hn_posts.json not found."
    )

# =========================
# VALIDATION
# =========================

if not posts:

    st.error(
        "No discovery data available."
    )

    st.stop()

# =====================================
# PAIN DETECTION
# =====================================

PAIN_WORDS = [
    "hate",
    "annoying",
    "frustrating",
    "difficult",
    "problem",
    "issue",
    "slow",
    "expensive",
    "broken",
    "manual"
]


def calculate_pain_score(text):

    text = str(text).lower()

    return sum(
        word in text
        for word in PAIN_WORDS
    )


def calculate_signal_score(post):

    return (
        post.get("pain_score", 0) * 3
        + post.get("comments", 0) / 10
        + post.get("score", 0) / 20
    )


for post in posts:

    combined_text = (
        post.get("title", "")
        + " "
        + post.get("text", "")
    )

    post["pain_score"] = calculate_pain_score(
        combined_text
    )

    post["signal_score"] = calculate_signal_score(
        post
    )

# =====================================
# SIDEBAR FILTERS
# =====================================

st.sidebar.header("Filters")

sources = sorted(
    list(
        set(
            post.get("source", "Unknown")
            for post in posts
        )
    )
)

selected_source = st.sidebar.selectbox(
    "Source",
    ["All"] + sources
)

subreddits = sorted(
    list(
        set(
            post.get("subreddit", "Unknown")
            for post in posts
        )
    )
)

selected_subreddit = st.sidebar.selectbox(
    "Subreddit",
    ["All"] + subreddits
)

min_comments = st.sidebar.slider(
    "Minimum Comments",
    0,
    500,
    0
)

min_pain_score = st.sidebar.slider(
    "Minimum Pain Score",
    0,
    10,
    0
)

# =====================================
# FILTER POSTS
# =====================================

filtered_posts = []

for post in posts:

    if (
        selected_source != "All"
        and post.get("source")
        != selected_source
    ):
        continue

    if (
        selected_subreddit != "All"
        and post.get(
            "subreddit",
            "Unknown"
        )
        != selected_subreddit
    ):
        continue

    if (
        post.get("comments", 0)
        < min_comments
    ):
        continue

    if (
        post.get("pain_score", 0)
        < min_pain_score
    ):
        continue

    filtered_posts.append(post)

# =====================================
# SORT BY SIGNAL SCORE
# =====================================

filtered_posts = sorted(
    filtered_posts,
    key=lambda x: x.get(
        "signal_score",
        0
    ),
    reverse=True
)

# =====================================
# SUMMARY METRICS
# =====================================
try:

    with open(
        "data/live/saved_opportunities.json",
        "r",
        encoding="utf-8"
    ) as f:

        saved_count = len(
            json.load(f)
        )

except:

    saved_count = 0


col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Posts",
        len(filtered_posts)
    )

with col2:

    avg_pain = round(
        sum(
            p.get("pain_score", 0)
            for p in filtered_posts
        ) / max(
            len(filtered_posts),
            1
        ),
        1
    )

    st.metric(
        "Avg Pain",
        avg_pain
    )

with col3:

    avg_signal = round(
        sum(
            p.get("signal_score", 0)
            for p in filtered_posts
        ) / max(
            len(filtered_posts),
            1
        ),
        1
    )

    st.metric(
        "Avg Signal",
        avg_signal
    )

with col4:

    st.metric(
        "Sources",
        len(
            set(
                p.get("source", "")
                for p in filtered_posts
            )
        )
    )

    with col5:

        st.metric(
        "Saved",
        saved_count
    )

st.divider()

# =====================================
# TOP SIGNALS
# =====================================

st.subheader("🔥 Top Signals")

top_posts = filtered_posts[:5]

for post in top_posts:

    st.markdown(
        f"""
        **{post.get('title', 'Untitled')}**

        Source: {post.get('source', 'Unknown')}
        | Signal Score: {round(post.get('signal_score', 0), 2)}
        """
    )

st.divider()

# =====================================
# DISCOVERY FEED
# =====================================

st.subheader("Discovery Feed")

if not filtered_posts:

    st.warning(
        "No posts match the selected filters."
    )

else:

    for idx, post in enumerate(filtered_posts):

        with st.container():

            st.subheader(
                post.get(
                    "title",
                    "Untitled"
                )
            )

            st.caption(
                f"Source: {post.get('source', 'Unknown')} | "
                f"Subreddit: {post.get('subreddit', 'N/A')}"
            )

            if post.get("text"):
                st.write(
                    post.get("text")
                )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Comments",
                    post.get(
                        "comments",
                        0
                    )
                )

            with col2:
                st.metric(
                    "Score",
                    post.get(
                        "score",
                        0
                    )
                )

            with col3:
                st.metric(
                    "Pain Score",
                    post.get(
                        "pain_score",
                        0
                    )
                )

            with col4:
                st.metric(
                    "Signal Score",
                    round(
                        post.get(
                            "signal_score",
                            0
                        ),
                        2
                    )
                )

            col_a, col_b = st.columns(2)

with col_a:

    if st.button(
        "💾 Save",
        key=f"save_{idx}"
    ):

        save_opportunity(post)

        st.success(
            "Opportunity Saved"
        )

with col_b:

    if st.button(
        "🤖 Analyze",
        key=f"analyze_{idx}"
    ):

        st.info(
            "AI Analysis Coming Soon"
        )

st.divider()