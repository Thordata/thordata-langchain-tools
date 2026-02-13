"""
Unified Agent Example - Works with ZhipuAI or OpenRouter

Simple example showing complete workflow with any LLM provider.

Usage:
    # With ZhipuAI
    export ZHIPU_API_KEY=your_key
    python examples/simple_agent_unified.py zhipu

    # With OpenRouter (when available)
    export OPENROUTER_API_KEY=your_key
    python examples/simple_agent_unified.py openrouter
"""

import os
import sys

if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from thordata_langchain_tools import ThordataSerpTool, ThordataMarkdownTool

load_dotenv()

if not os.getenv("THORDATA_SCRAPER_TOKEN"):
    print("❌ Error: Set THORDATA_SCRAPER_TOKEN in your .env file")
    sys.exit(1)

provider = sys.argv[1] if len(sys.argv) > 1 else "zhipu"

# Search and scrape
serp = ThordataSerpTool()
results = serp.invoke({"query": "Python web scraping", "num": 1})
url = results["organic"][0]["link"]

markdown = ThordataMarkdownTool()
content = markdown.invoke({"url": url, "max_chars": 3000})

# Summarize
if provider == "zhipu" and os.getenv("ZHIPU_API_KEY"):
    from zhipuai import ZhipuAI

    client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": f"Summarize: {content[:2000]}"}],
    )
    print(response.choices[0].message.content)
elif provider == "openrouter" and os.getenv("OPENROUTER_API_KEY"):
    from openai import OpenAI

    client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )
    response = client.chat.completions.create(
        model="google/gemini-2.0-flash:free",
        messages=[{"role": "user", "content": f"Summarize: {content[:2000]}"}],
    )
    print(response.choices[0].message.content)
else:
    print("⚠️  No LLM provider configured. Showing content only:")
    print(content[:500])
