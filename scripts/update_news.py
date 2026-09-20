import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEEDS = [
    (
        "NHK 経済",
        "https://www.nhk.or.jp/rss/news/cat5.xml"
    ),
    (
        "Google News 日本経済",
        "https://news.google.com/rss/search?q=%E6%97%A5%E6%9C%AC%E7%B5%8C%E6%B8%88&hl=ja&gl=JP&ceid=JP:ja"
    ),
]


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "News3min/1.0"}
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read()


items = []
seen = set()

for source, url in FEEDS:
    try:
        root = ET.fromstring(fetch(url))

        for item in root.findall(".//item")[:10]:

            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            published = (item.findtext("pubDate") or "").strip()

            if title and link and title not in seen:
                seen.add(title)

                items.append({
                    "title": title,
                    "link": link,
                    "published": published,
                    "source": source
                })

    except Exception as e:
        print(f"feed failed: {source}: {e}")


payload = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "articles": items[:20]
}


with open(
    "data/news.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        payload,
        f,
        ensure_ascii=False,
        indent=2
    )


print(
    f"collected {len(items[:20])} headlines"
)
