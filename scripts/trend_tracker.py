import json
from datetime import datetime
from pathlib import Path


def save_snapshot(opportunities):

    Path("data/history").mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"data/history/{timestamp}.json"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            opportunities,
            f,
            indent=4,
            ensure_ascii=False
        )

    return filename