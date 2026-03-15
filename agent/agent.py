import requests
import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
def summarize_with_groq(title):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": f"Write a 2-3 sentence summary for an AI news article titled: '{title}'. Make it informative and engaging for a tech audience."
            }
        ]
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json=data, headers=headers
    )
    result = response.json()
    return result["choices"][0]["message"]["content"]

def save_to_supabase(title, summary, source, source_url):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
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
        f"{SUPABASE_URL}/rest/v1/posts",
        json=data, headers=headers
    )
    print(f"Save status: {response.status_code}")
    if response.status_code == 201:
        print(f"✓ Saved draft: {title}")
    else:
        print(f"✗ Error: {response.text}")

def run():
    # Manual articles for testing — real scraping comes next
    articles = [
        {
            "title": "Claude 3.5 Sonnet: Anthropic's Most Intelligent Model",
            "url": "https://www.anthropic.com/news/claude-3-5-sonnet"
        },
        {
            "title": "OpenAI releases GPT-4o with vision and voice capabilities",
            "url": "https://openai.com/blog/gpt-4o"
        },
        {
            "title": "Google DeepMind introduces Gemini 2.0 for agentic AI tasks",
            "url": "https://deepmind.google/discover/blog"
        }
    ]

    for article in articles:
        print(f"Processing: {article['title']}")
        summary = summarize_with_groq(article['title'])
        save_to_supabase(
            title=article['title'],
            summary=summary,
            source="Anthropic" if "anthropic" in article['url'] else "OpenAI" if "openai" in article['url'] else "Google DeepMind",
            source_url=article['url']
        )

    print("\nDone! Check Supabase table editor.")

run()