import os
import urllib.request
import urllib.parse
import json
from html.parser import HTMLParser
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = str(os.environ.get("GROQ_API_KEY", "")).strip()
SUPABASE_URL = str(os.environ.get("SUPABASE_URL", "")).strip()
SUPABASE_KEY = str(os.environ.get("SUPABASE_KEY", "")).strip()

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_text = ""
        self.in_anchor = False
        self.current_href = ""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.in_anchor = True
            self.current_text = ""
            for attr in attrs:
                if attr[0] == "href":
                    self.current_href = attr[1]

    def handle_data(self, data):
        if self.in_anchor:
            self.current_text += data.strip()

    def handle_endtag(self, tag):
        if tag == "a":
            self.in_anchor = False
            if self.current_text and len(self.current_text) > 20:
                self.links.append({
                    "title": self.current_text,
                    "href": self.current_href
                })

def scrape_anthropic():
    url = "https://www.anthropic.com/news"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8")
        parser = LinkParser()
        parser.feed(html)
        articles = []
        for link in parser.links:
            href = link["href"]
            title = link["title"].replace("\n", " ").strip()
            if "/news/" in href and len(title) > 15 and len(title) < 100:
                full_url = "https://www.anthropic.com" + href if href.startswith("/") else href
                articles.append({
                    "title": title,
                    "url": full_url,
                    "source": "Anthropic"
                })
        return articles[:3]
    except Exception as e:
        print("Scrape error: " + str(e))
        return []

def scrape_huggingface():
    url = "https://huggingface.co/blog"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8")
        parser = LinkParser()
        parser.feed(html)
        articles = []
        for link in parser.links:
            href = link["href"]
            title = link["title"].replace("\n", " ").strip()
            if "/blog/" in href and len(title) > 15:
                full_url = "https://huggingface.co" + href if href.startswith("/") else href
                articles.append({
                    "title": title,
                    "url": full_url,
                    "source": "HuggingFace"
                })
        return articles[:3]
    except Exception as e:
        print("Scrape error: " + str(e))
        return []

def summarize_with_groq(title):
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": "Write a 2-3 sentence summary for an AI news article titled: " + title
            }
        ]
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
            print("Saved: " + title)
    except Exception as e:
        print("Error saving: " + str(e))

def run():
    print("Scraping Anthropic...")
    anthropic_articles = scrape_anthropic()
    print("Scraping HuggingFace...")
    hf_articles = scrape_huggingface()

    all_articles = anthropic_articles + hf_articles
    print("Found " + str(len(all_articles)) + " articles")

    for article in all_articles:
        if already_exists(article["title"]):
            print("Skipping: " + article["title"])
            continue
        print("Processing: " + article["title"])
        summary = summarize_with_groq(article["title"])
        save_to_supabase(
            title=article["title"],
            summary=summary,
            source=article["source"],
            source_url=article["url"]
        )

    print("Done!")

run()