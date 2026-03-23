import json
import os
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

RSS_URL = os.getenv("RSS_URL")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

if not RSS_URL:
    raise ValueError("Missing RSS_URL environment variable")

if not DISCORD_WEBHOOK_URL:
    raise ValueError("Missing DISCORD_WEBHOOK_URL environment variable")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SEEN_FILE = DATA_DIR / "talkwalker_seen.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def clean_text(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def load_seen() -> set[str]:
    if not SEEN_FILE.exists():
        return set()

    try:
        data = json.loads(SEEN_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {str(item) for item in data}
        return set()
    except Exception:
        return set()


def save_seen(seen: set[str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(
        json.dumps(sorted(seen), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def fetch_rss(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def parse_rss(xml_text: str) -> list[dict[str, str]]:
    root = ET.fromstring(xml_text)
    items: list[dict[str, str]] = []

    for item in root.findall("./channel/item"):
        title = clean_text(item.findtext("title"))
        link = clean_text(item.findtext("link"))
        description = clean_text(item.findtext("description"))
        guid = clean_text(item.findtext("guid"))

        unique_id = guid or link or title
        if not unique_id:
            continue

        if title == "There is currently no rss feed item":
            continue

        items.append(
            {
                "id": unique_id,
                "title": title,
                "link": link,
                "description": description,
            }
        )

    return items


def send_discord_message(message: str) -> None:
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=30)
    response.raise_for_status()


def format_item(item: dict[str, str]) -> str:
    lines: list[str] = []

    if item["title"]:
        lines.append(f"**{item['title']}**")

    if item["description"]:
        desc = item["description"]
        if len(desc) > 400:
            desc = desc[:400].rstrip() + "..."
        lines.append(desc)

    if item["link"]:
        lines.append(item["link"])

    return "\n".join(lines)


def main() -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        seen = load_seen()
        xml_text = fetch_rss(RSS_URL)
        items = parse_rss(xml_text)

        if not items:
            print("No RSS items found.")
            return

        new_items = [item for item in items if item["id"] not in seen]

        if not new_items:
            print("No new items.")
            return

        for item in new_items:
            message = "New Talkwalker match:\n\n" + format_item(item)
            send_discord_message(message)
            seen.add(item["id"])
            time.sleep(1)

        save_seen(seen)
        print(f"Sent {len(new_items)} new item(s) to Discord.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()