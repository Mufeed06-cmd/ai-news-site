import requests
import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def summarize_with_groq(title):
    headers = {
        "Authorization": "Bearer " + GROQ_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": "Write a 2-3 sentence summary for an AI news article titled: '" + title + "'. Make it informative and engaging for a tech audience."
            }
        ]
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json=data,
        headers=headers
    )
    result = response.json()
    return result["choices"][0]["message"]["content"]

def save_to_supabase(title, summary, source, source_url):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": "Bearer " + SUPABASE_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    data = {
        "title": title,
        "summary": summary,
        "source": source,
        "source_url": source_url,
        "status": "draft"
    }
    response = requests.post(
        SUPABASE_URL + "/rest/v1/posts",
        json=data,
        headers=headers
    )
    print("Save status: " + str(response.status_code))
    if response.status_code == 201:
        print("Saved: " + title)
    else:
        print("Error: " + response.text)

def run():
    articles = [
        {
            "title": "Claude 3.5 Sonnet: Anthropic Most Intelligent Model",
            "url": "https://www.anthropic.com/news/claude-3-5-sonnet",
            "source": "Anthropic"
        },
        {
            "title": "OpenAI releases GPT-4o with vision and voice capabilities",
            "url": "https://openai.com/blog/gpt-4o",
            "source": "OpenAI"
        },
        {
            "title": "Google DeepMind introduces Gemini 2.0 for agentic AI",
            "url": "https://deepmind.google/discover/blog",
            "source": "Google DeepMind"
        }
    ]

    for article in articles:
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