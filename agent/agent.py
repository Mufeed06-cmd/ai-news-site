import os
import re
import urllib.request
import urllib.parse
import json
from html.parser import HTMLParser
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = str(os.environ.get("GROQ_API_KEY", "")).strip()
SUPABASE_URL = str(os.environ.get("SUPABASE_URL", "")).strip()
SUPABASE_KEY = str(os.environ.get("SUPABASE_KEY", "")).strip()

class ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.articles = []
        self.in_anchor = False
        self.current_href = ""
        self.current_text = ""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.in_anchor = True
            self.current_text = ""
            for attr in attrs:
                if attr[0] == "href":
                    self.current_href = attr[1]

    def handle_data(self, data):
        if self.in_anchor:
            self.current_text += data

    def handle_endtag(self, tag):
        if tag == "a":
            self.in_anchor = False
            title = self.current_text.strip()
            title = " ".join(title.split())

            # Clean messy parts
            title = re.sub(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+,\s+\d{4}', '', title)
            title = re.sub(r'\d+\s+days?\s+ago', '', title)
            title = re.sub(r'\d+\s+hours?\s+ago', '', title)
            title = re.sub(r'Announcements', '', title)
            title = re.sub(r'\d+\s*•\s*\d+', '', title)
            title = re.sub(r'•\s*\d+', '', title)
            title = re.sub(r'\s*\d+$', '', title)
            title = re.sub(r'\*+', '', title)
            title = re.sub(r'^\s*•\s*', '', title)
            title = title.strip()
            title = " ".join(title.split())

            if len(title) > 20 and len(title) < 120:
                self.articles.append({
                    "title": title,
                    "href": self.current_href
                })

def scrape_source(url, base_url, path_keyword, source_name):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="ignore")

        parser = ArticleParser()
        parser.feed(html)

        seen = set()
        articles = []
        for item in parser.articles:
            href = item["href"]
            title = item["title"]

            if path_keyword not in href:
                continue
            if title in seen:
                continue
            if len(title) < 20:
                continue

            seen.add(title)
            full_url = base_url + href if href.startswith("/") else href
            articles.append({
                "title": title,
                "url": full_url,
                "source": source_name
            })

        return articles[:3]
    except Exception as e:
        print(f"Scrape error for {source_name}: {str(e)}")
        return []

def summarize_with_groq(title):
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": f"Write a 2-3 sentence engaging summary for an AI news article titled: '{title}'. Be informative and clear for a general tech audience."
            }
        ],
        "max_tokens": 150
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", "Bearer " + GROQ_API_KEY)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0")

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"]

def already_exists(title):
    url = SUPABASE_URL + "/rest/v1/posts?title=eq." + urllib.parse.quote(title) + "&select=id"
    req = urllib.request.Request(url, method="GET")
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", "Bearer " + SUPABASE_KEY)
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
    return len(result) > 0

def save_to_supabase(title, summary, source, source_url):
    url = SUPABASE_URL + "/rest/v1/posts"
    payload = json.dumps({
        "title": title,
        "summary": summary,
        "source": source,
        "source_url": source_url,
        "status": "draft"
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", "Bearer " + SUPABASE_KEY)
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=minimal")

    try:
        with urllib.request.urlopen(req) as response:
            print(f"Saved: {title}")
    except Exception as e:
        print(f"Error saving: {str(e)}")

def run():
    print("Scraping news sources...")

    all_articles = []

    anthropic = scrape_source(
        "https://www.anthropic.com/news",
        "https://www.anthropic.com",
        "/news/",
        "Anthropic"
    )
    all_articles.extend(anthropic)
    print(f"Anthropic: {len(anthropic)} articles")

    hf = scrape_source(
        "https://huggingface.co/blog",
        "https://huggingface.co",
        "/blog/",
        "HuggingFace"
    )
    all_articles.extend(hf)
    print(f"HuggingFace: {len(hf)} articles")

    print(f"\nTotal found: {len(all_articles)}")
    saved = 0

    for article in all_articles:
        if already_exists(article["title"]):
            print(f"Skipping (exists): {article['title'][:50]}...")
            continue
        print(f"Processing: {article['title'][:60]}...")
        try:
            summary = summarize_with_groq(article["title"])
            save_to_supabase(
                title=article["title"],
                summary=summary,
                source=article["source"],
                source_url=article["url"]
            )
            saved += 1
        except Exception as e:
            print(f"Error: {str(e)}")
            continue

    print(f"\nDone! Saved {saved} new articles.")

run()