"""
Simple LangChain Agent Example

Demonstrates using Thordata tools with a LangChain agent to:
1. Search for information
2. Scrape a webpage
3. Summarize the content

Requirements:
    pip install langchain-openai openai

Usage:
    export OPENAI_API_KEY=your_key
    python examples/simple_agent.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Check required environment variables
if not os.getenv("THORDATA_SCRAPER_TOKEN"):
    print("❌ Error: Set THORDATA_SCRAPER_TOKEN in your .env file")
    sys.exit(1)

if not os.getenv("OPENAI_API_KEY"):
    print("❌ Error: Set OPENAI_API_KEY in your .env file")
    sys.exit(1)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from thordata_langchain_tools import ThordataSerpTool, ThordataScrapeTool


def search_for_homepage(query: str) -> str:
    """Use SERP tool to find a homepage URL."""
    print(f"🔍 Searching for: '{query}'")
    
    serp_tool = ThordataSerpTool()
    results = serp_tool.invoke({
        "query": query,
        "engine": "google",
        "num": 3,
    })

    organic = results.get("organic", [])
    for item in organic:
        link = item.get("link", "")
        if link and "thordata" in link.lower():
            return link
    
    # Return first result if no thordata link found
    if organic:
        return organic[0].get("link", "")
    
    raise RuntimeError("No results found")


def scrape_page(url: str) -> str:
    """Use Scrape tool to get page content."""
    print(f"📄 Scraping: {url}")
    
    scrape_tool = ThordataScrapeTool()
    html = scrape_tool.invoke({
        "url": url,
        "js_render": False,
        "max_length": 5000,
    })
    
    return html


def summarize_with_llm(html: str, topic: str) -> str:
    """Use LLM to summarize the content."""
    print("🤖 Summarizing with LLM...")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""You are a helpful assistant that summarizes web content.

Based on the following HTML content, provide a brief summary about {topic}.
Focus on the key products, services, or features mentioned.

Provide your summary in 3-5 bullet points.

HTML Content:
{html[:4000]}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def main():
    print("=" * 60)
    print("🚀 Thordata LangChain Agent Demo")
    print("=" * 60)
    print()

    try:
        # Step 1: Search for Thordata
        url = search_for_homepage("Thordata proxy network official site")
        print(f"   Found URL: {url}\n")

        # Step 2: Scrape the page
        html = scrape_page(url)
        print(f"   Scraped {len(html)} characters\n")

        # Step 3: Summarize
        summary = summarize_with_llm(html, "Thordata's services")
        
        print()
        print("=" * 60)
        print("📋 Summary:")
        print("=" * 60)
        print(summary)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()