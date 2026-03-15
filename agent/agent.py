import os
import urllib.request
import urllib.parse
import json

GROQ_API_KEY = str(os.environ.get("GROQ_API_KEY", "")).strip()
SUPABASE_URL = str(os.environ.get("SUPABASE_URL", "")).strip()
SUPABASE_KEY = str(os.environ.get("SUPABASE_KEY", "")).strip()

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
    articles = [
        {
            "title": "Claude 3.5 Sonnet: Anthropic Most Intelligent Model",
            "url": "https://www.anthropic.com/news/claude-3-5-sonnet",
            "source": "Anthropic"
        },
        {
            "title": "OpenAI releases GPT-4o with vision and voice",
            "url": "https://openai.com/blog/gpt-4o",
            "source": "OpenAI"
        },
        {
            "title": "Google DeepMind introduces Gemini 2.0",
            "url": "https://deepmind.google/discover/blog",
            "source": "Google DeepMind"
        }
    ]

    for article in articles:
        if already_exists(article["title"]):
            print("Already exists, skipping: " + article["title"])
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