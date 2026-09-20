import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEEDS = [
    ("NHK 経済", "https://www.nhk.or.jp/rss/news/cat5.xml"),
    ("Google News 日本経済", "https://news.google.com/rss/search?q=%E6%97%A5%E6%9C%AC%E7%B5%8C%E6%B8%88&hl=ja&gl=JP&ceid=JP:ja"),
]

KEYWORDS = {
    "日銀":10,"政策金利":10,"利上げ":9,"利下げ":9,"金融政策":9,
    "円安":8,"円高":8,"為替":8,"ドル円":8,"物価":8,"インフレ":8,
    "GDP":8,"賃金":7,"実質賃金":8,"消費者物価":9,"CPI":9,
    "失業率":7,"雇用":6,"景気":7,"景気動向":8,"国債":7,
    "財務省":6,"政府":5,"税":6,"減税":7,"増税":7,"予算":6,
    "貿易":6,"輸出":6,"輸入":6,"原油":6,"電気料金":6,"ガソリン":6,
    "企業":4,"決算":5,"倒産":6,"株価":5,"日経平均":6,"TOPIX":6,
    "半導体":5,"AI":4,"米国":3,"中国":3,"関税":7
}
EXCLUDE = ["スポーツ","プロ野球","サッカー","競馬","芸能","映画","ドラマ","サイン会","書店","ゲーム","漫画","アニメ"]
CATEGORIES = [
    ("金融政策",["日銀","政策金利","利上げ","利下げ","金融政策"]),
    ("為替・金利",["円安","円高","為替","ドル円","国債","長期金利"]),
    ("物価・家計",["物価","インフレ","消費者物価","CPI","電気料金","ガソリン","賃金","実質賃金"]),
    ("景気・雇用",["GDP","景気","景気動向","雇用","失業率"]),
    ("企業・産業",["企業","決算","倒産","半導体","AI"]),
    ("政策・財政",["財務省","政府","税","減税","増税","予算","関税"])
]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"News3min/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()

def score(title, source):
    if any(x in title for x in EXCLUDE):
        return -20
    s = sum(v for k,v in KEYWORDS.items() if k.lower() in title.lower())
    if source == "NHK 経済":
        s += 2
    return s if s else -5

def category(title):
    for name, words in CATEGORIES:
        if any(x in title for x in words):
            return name
    return "経済ニュース"

items, seen = [], set()

for source, url in FEEDS:
    try:
        root = ET.fromstring(fetch(url))
        for item in root.findall(".//item")[:15]:
            title = re.sub(r"\s+"," ",(item.findtext("title") or "").strip())
            link = (item.findtext("link") or "").strip()
            published = (item.findtext("pubDate") or "").strip()
            key = title.lower()
            if not title or not link or key in seen:
                continue
            seen.add(key)
            items.append({
                "title":title,"link":link,"published":published,
                "source":source,"score":score(title,source),
                "category":category(title)
            })
    except Exception as e:
        print(f"feed failed: {source}: {e}")

items.sort(key=lambda x:x["score"], reverse=True)
payload = {
    "updated_at":datetime.now(timezone.utc).isoformat(),
    "articles":items[:20],
    "top_articles":[x for x in items if x["score"] > 0][:3]
}
with open("data/news.json","w",encoding="utf-8") as f:
    json.dump(payload,f,ensure_ascii=False,indent=2)

print(f"collected {len(items)} headlines")
