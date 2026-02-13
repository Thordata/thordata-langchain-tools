"""
OpenRouter Agent Example with Thordata Tools

Demonstrates using Thordata tools with OpenRouter free models.
Complete workflow: search -> scrape -> summarize.

Available free models (try in order):
- google/gemini-2.0-flash:free (Multimodal, 1M context)
- deepseek/deepseek-r1:free (Strong reasoning)
- microsoft/phi-4:free (Microsoft open source)
- meta-llama/llama-3.3-70b-instruct:free (GPT-4 level, may be rate-limited)

Requirements:
    pip install openai

Usage:
    export OPENROUTER_API_KEY=your_key
    python examples/openrouter_agent.py
"""

import os
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv

load_dotenv()

if not os.getenv("THORDATA_SCRAPER_TOKEN"):
    print("❌ Error: Set THORDATA_SCRAPER_TOKEN in your .env file")
    sys.exit(1)

if not os.getenv("OPENROUTER_API_KEY"):
    print("❌ Error: Set OPENROUTER_API_KEY in your .env file")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("❌ Error: Please install openai: pip install openai")
    sys.exit(1)

from thordata_langchain_tools import ThordataSerpTool, ThordataMarkdownTool


def search_and_scrape(query: str):
    """Search and scrape content."""
    print(f"🔍 Searching for: '{query}'")
    
    serp = ThordataSerpTool()
    results = serp.invoke({"query": query, "num": 1})
    
    if "error" in results or not results.get("organic"):
        print("   ❌ Search failed")
        return None, None
    
    url = results["organic"][0]["link"]
    title = results["organic"][0].get("title", "")
    print(f"   ✓ Found: {title}")
    print(f"   🔗 {url}")
    
    print(f"📝 Converting to Markdown...")
    markdown = ThordataMarkdownTool()
    content = markdown.invoke({"url": url, "max_chars": 6000})
    
    if content.startswith("Error"):
        print("   ❌ Scrape failed")
        return None, None
    
    print(f"   ✓ Converted {len(content)} characters")
    return content, title


def summarize_with_openrouter(content: str, topic: str):
    """Summarize using OpenRouter free models."""
    # Use verified working free models
    models = [
        "openrouter/free",  # Default free model
        "stepfun/step-3.5-flash:free",
        "qwen/qwen3-coder:free",
        "deepseek/deepseek-r1-0528:free",
        "z-ai/glm-4.5-air:free",
    ]
    
    client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )
    
    prompt = f"""Summarize the following content about "{topic}" in 3-5 bullet points:

{content[:5000]}

Summary:"""
    
    for model in models:
        try:
            print(f"🤖 Trying {model}...")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            print(f"   ✓ Success!")
            return response.choices[0].message.content
        except Exception as e:
            error = str(e)
            if "rate-limited" in error or "429" in error:
                print(f"   ⚠️  Rate-limited, trying next...")
                continue
            print(f"   ⚠️  Error: {error[:80]}...")
            continue
    
    return None


def main():
    print("=" * 70)
    print("🚀 Thordata + OpenRouter Agent Demo")
    print("=" * 70)
    print()
    
    try:
        content, title = search_and_scrape("Thordata proxy network features")
        if not content:
            sys.exit(1)
        
        print()
        summary = summarize_with_openrouter(content, title or "Thordata")
        
        if not summary:
            print("❌ All models failed. Content preview:")
            print(content[:500])
            sys.exit(1)
        
        print()
        print("=" * 70)
        print("📋 Summary:")
        print("=" * 70)
        print(summary)
        print()
        print("=" * 70)
        print("✅ Demo completed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
