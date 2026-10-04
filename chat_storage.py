import json
import os
import re
from datetime import datetime


# Store user chats outside the installed application directory.
BASE_DIR = os.path.expanduser(
    "~/.local/share/pravithai"
)

CHATS_DIR = os.path.join(
    BASE_DIR,
    "chats",
)


def ensure_chats_directory():
    os.makedirs(
        CHATS_DIR,
        exist_ok=True,
    )


def safe_filename(name):
    name = name.strip()

    if not name:
        name = "Untitled Chat"

    name = re.sub(
        r"[^a-zA-Z0-9 _-]",
        "",
        name,
    )

    name = re.sub(
        r"\s+",
        " ",
        name,
    )

    return name[:80].strip() or "Untitled Chat"


def save_chat(title, messages):
    ensure_chats_directory()

    safe_title = safe_filename(title)

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"{safe_title}_{timestamp}.json"
    )

    path = os.path.join(
        CHATS_DIR,
        filename,
    )

    data = {
        "title": title,
        "created": datetime.now().isoformat(),
        "messages": messages,
    }

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return path


def load_chat(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def list_chats():
    ensure_chats_directory()

    chats = []

    for filename in os.listdir(
        CHATS_DIR
    ):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(
            CHATS_DIR,
            filename,
        )

        try:
            data = load_chat(path)

            chats.append(
                {
                    "path": path,
                    "title": data.get(
                        "title",
                        "Untitled Chat",
                    ),
                    "created": data.get(
                        "created",
                        "",
                    ),
                }
            )

        except Exception:
            continue

    chats.sort(
        key=lambda chat: chat["created"],
        reverse=True,
    )

    return chats


def delete_chat(path):
    if os.path.isfile(path):
        os.remove(path)